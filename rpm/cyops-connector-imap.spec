Name: cyops-connector-%{connector_name}
Prefix: /opt/%{name}
Version: %{_version}
Release: %{build_no}%{dist}
License: Commercial
Vendor: Fortinet
Packager: devops-fortisoar@fortinet.com
URL: https://www.fortinet.com
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-root

Requires: cyops-integrations, lsof, cyops-api, cyops-connector-cyops_utilities >= 3.0.0

Summary: FortiSOAR %{connector_display_name} Connector
%description
FortiSOAR %{connector_display_name} Connector

#%global
%define integrations_dir /opt/cyops-integrations
%define venv_name .env
%define venv_install_dir %{integrations_dir}/%{venv_name}
%define venv_bin %{venv_install_dir}/bin
%define venv_python %{venv_bin}/python3
%define venv_pip %{venv_python} %{venv_bin}/pip3 install
%define venv_site_packages %{venv_install_dir}/lib/python3.4/site-packages/

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}%{prefix}/
cp %{connector_name}.tgz %{buildroot}%{prefix}/
if [ -f compatibility.txt ]; then
    cp install.py %{buildroot}%{prefix}/
    cp compatibility.txt %{buildroot}%{prefix}/
fi
echo "compatibility_check is %{compatibility_check}"

%clean
%pre
mkdir -p %{install_log_dir}
{
    set -x
    echo "Date: `date`"
    echo "%{name}: pre"
    echo "============================================"
#    if [ $1 = 1 ]; then
#        # Write pre install actions here
#        echo ""
#    elif [ $1 -gt 1 ]; then
#        # Write pre upgrade actions here
#        echo ""
#    fi
    echo "============================================"
} >> %{install_log_dir}/%{install_log_file} 2>&1
# %pre ends here

%post
mkdir -p %{install_log_dir}
{
    set -x
    echo "Date: `date`"
    echo "%{name}: post"
    echo "============================================"

    restorecon -R %{prefix}

    if [ $1 = 1 ]; then
        # Write post install actions here

        # Copy connector
        cp %{prefix}/%{connector_name}.tgz %{integrations_dir}/integrations/connectors/

        # Extract Connector
        cd %{integrations_dir}/integrations
        sudo -u nginx %{venv_python} manage.py connectors

        #Remove tgz
        rm -rf %{integrations_dir}/integrations/connectors/%{connector_name}.tgz
    elif [ $1 -gt 1 ]; then
        # Write post upgrade action here

        # Extract Connector
        if [ -f %{prefix}/compatibility.txt ]; then
            cd %{prefix}
            compatibility=`cat compatibility.txt`
            sudo -u nginx %{venv_python} install.py --name %{connector_name} --compatibility ${compatibility}
        else
            # Copy connector
            cp %{prefix}/%{connector_name}.tgz %{integrations_dir}/integrations/connectors/

            # Extract Connector
            cd %{integrations_dir}/integrations
            sudo -u nginx %{venv_python} manage.py connectors

            #Remove tgz
            rm -rf %{integrations_dir}/integrations/connectors/%{connector_name}.tgz
        fi
    fi

    # Install requirements.txt
    mod_version=`echo %{version} | sed 's/\./_/g'`
    connector_name_version=%{connector_name}_${mod_version}
    if [ -f %{integrations_dir}/integrations/connectors/${connector_name_version}/requirements.txt ]; then
        rm -rf ~/.cache/pip/
        export LC_ALL="en_US.UTF-8"
        # some dependencies installed as root cause issue during library upgrade
        owner_check=`ls -al %{venv_site_packages} | grep "root"`
        if [ "$owner_check" = "" ]; then
            echo "no dependencies owned by root"
        else
            echo "some files owned by root. changing ownership"
            chown -R nginx:nginx %{venv_site_packages}
        fi
        sudo -u nginx %{venv_pip} -b ./tmp -r %{integrations_dir}/integrations/connectors/${connector_name_version}/requirements.txt
    fi
    find %{buildroot} -name "RECORD" -exec rm -rf {} \;
    rm -rf ./tmp

    restorecon -R %{prefix}

    echo "============================================"
} >> %{install_log_dir}/%{install_log_file} 2>&1
# post ends here

%postun
mkdir -p %{install_log_dir}
{
    set -x
    echo "Date: `date`"
    echo "%{name}: postun"
    echo "============================================"
    run_os_user="nginx"
    if id fortisoar 2>/dev/null; then
        run_os_user="fortisoar"
    fi
    if [ $1 = 0 ]; then
        # Write post remove actions here
        cd %{integrations_dir}/integrations
        sudo -u nginx %{venv_python} manage.py deleteconnector %{connector_name} %{version}
        # Clean up
        rm -rf %{prefix}
    fi
    echo "============================================"
} >> %{install_log_dir}/%{install_log_file} 2>&1
# postun ends here

%files
%{prefix}
%attr(0755, root, root) %{prefix}/%{connector_name}.tgz
%exclude %{prefix}/*.pyc
%exclude %{prefix}/*.pyo
%if "%{compatibility_check}" == "1"
%attr(0755, root, root) %{prefix}/install.py
%attr(0755, root, root) %{prefix}/compatibility.txt
%endif