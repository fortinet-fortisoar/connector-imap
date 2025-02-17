#!/bin/bash -ex
version=$1
build_num=$2
src_dir=$3
pkg_name=$4
connector_code_folder=$5
connector_display_name=$6
spec_file=$7
system_connector=$8

# Ex:
# version=1.0.0.0
# build_num=123
# src_dir=<path/including/repository name>
# pkg_name=cyops-arcsight
# connector_code_folder=arcsight [name of the folder which contains connector code]

if [[ -z "$version" || -z "$build_num" || \
      -z "$src_dir" || -z "$install_log_dir" || \
      -z "$install_log_file" || -z "$pkg_name" || \
      -z "$connector_code_folder" || -z "$connector_display_name" || \
      -z "$spec_file" ]]; then
	echo "You are missing variables";
	exit 1 ;
fi

RPM_BUILD_ROOT="${HOME}/rpmbuild"
RPM_SPEC_DIR="${RPM_BUILD_ROOT}/SPECS"
RPM_SOURCE_DIR="${RPM_BUILD_ROOT}/SOURCES"

mydir=$(pwd)
base_dir="$(dirname "$mydir")"
tmp_dir="${base_dir}/build"
tar_name="cyops-${pkg_name}-${version}.tar.gz"
#spec_file="$src_dir/rpm/${pkg_name}.spec"

create_connector_tar(){
    rm -rf ${tmp_dir}
    mkdir -p $tmp_dir/${pkg_name}-${version}
    cp -R $src_dir/rpm $tmp_dir/${pkg_name}-${version}/
    tar czf $tmp_dir/${connector_code_folder}.tgz -C $src_dir ${connector_code_folder}
    cp $tmp_dir/${connector_code_folder}.tgz $tmp_dir/${pkg_name}-${version}
    mv $tmp_dir/${pkg_name}-${version} $tmp_dir/cyops-${pkg_name}-${version}
    tar czf $tmp_dir/${tar_name} -C ${tmp_dir} cyops-${pkg_name}-${version}
    mv ${tmp_dir}/${tar_name} ${RPM_SOURCE_DIR}
}

cleanup(){
    dirs="BUILD BUILDROOT SOURCES RPMS/x86_64 SRPMS"
    for i in $dirs; do
        rm -rf $RPM_BUILD_ROOT/$i/${pkg_name}-${version}*
    done
}

# Clean up previous builds
cleanup

create_connector_tar

rpmbuild --clean -ba \
    --define "install_log_dir $install_log_dir" \
    --define "install_log_file $install_log_file" \
    --define "connector_name $connector_code_folder" \
    --define "connector_display_name $connector_display_name" \
    --define "_version ${version}" \
    --define "build_no ${build_num}" \
    --define "system_connector ${system_connector}" ${spec_file}
