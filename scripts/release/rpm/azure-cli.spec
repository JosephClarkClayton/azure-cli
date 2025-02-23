# RPM spec file for Azure CLI
# Definition of macros used - https://fedoraproject.org/wiki/Packaging:RPMMacros?rd=Packaging/RPMMacros

%global __python %{__python3}
# Turn off python byte compilation
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

# .el7.centos -> .el7
%if 0%{?rhel}
  %define dist .el%{?rhel}
%endif

%define python_cmd python3

%define name           azure-cli
%define release        1%{?dist}
%define version        %{getenv:CLI_VERSION}
%define repo_path      %{getenv:REPO_PATH}
%define cli_lib_dir    %{_libdir}/az

Summary:        Azure CLI
License:        MIT
Name:           %{name}
Version:        %{version}
Release:        %{release}
Url:            https://docs.microsoft.com/cli/azure/install-azure-cli
BuildArch:      x86_64
Requires:       %{python_cmd}

BuildRequires:  gcc, libffi-devel, openssl-devel, perl
BuildRequires:  %{python_cmd}-devel

%global _python_bytecompile_errors_terminate_build 0

%description
A great cloud needs great tools; we're excited to introduce Azure CLI,
 our next generation multi-platform command line experience for Azure.

%prep
%install
# Create a fully instantiated virtual environment, ready to use the CLI.
%{python_cmd} -m venv %{buildroot}%{cli_lib_dir}
source %{buildroot}%{cli_lib_dir}/bin/activate
%{python_cmd} -m pip install --upgrade pip==21.0.1
source %{repo_path}/scripts/install_full.sh

deactivate

# Fix up %{buildroot} appearing in some files...
for d in %{buildroot}%{cli_lib_dir}/bin/*; do perl -p -i -e "s#%{buildroot}##g" $d; done;

# Create executable
mkdir -p %{buildroot}%{_bindir}
python_version=$(ls %{buildroot}%{cli_lib_dir}/lib/ | head -n 1)
printf "#!/usr/bin/env bash\nAZ_INSTALLER=RPM PYTHONPATH=%{cli_lib_dir}/lib/${python_version}/site-packages /usr/bin/%{python_cmd} -sm azure.cli \"\$@\"" > %{buildroot}%{_bindir}/az
rm %{buildroot}%{cli_lib_dir}/bin/python* %{buildroot}%{cli_lib_dir}/bin/pip*

# Remove unused Network SDK API versions
pushd %{buildroot}%{cli_lib_dir}/lib/${python_version}/site-packages/azure/mgmt/network/ > /dev/null
rm -rf v2016_09_01 v2016_12_01 v2017_03_01 v2017_06_01 v2017_08_01 v2017_09_01 v2017_11_01 v2018_02_01 v2018_04_01 v2018_06_01 v2018_10_01 v2018_12_01 v2019_04_01 v2019_08_01 v2019_09_01 v2019_11_01 v2019_12_01 v2020_03_01
popd > /dev/null

# Set up tab completion
mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d/
cat %{repo_path}/az.completion > %{buildroot}%{_sysconfdir}/bash_completion.d/azure-cli

%files
%exclude %{cli_lib_dir}/bin/
%attr(-,root,root) %{cli_lib_dir}
%config(noreplace) %{_sysconfdir}/bash_completion.d/azure-cli
%attr(0755,root,root) %{_bindir}/az
