%define revision 09786

# The source for this package was pulled from upstream's subversion (svn).
# Use the following commands to generate the tarball:
# svn export -r 8899 http://svn.wildfiregames.com/public/ps/trunk/ 0ad-r8899
# find 0ad-r8899 \( -name "*.dll" -or -name "*.exe" -or -name "*.lib" -or -name "*.bat" \) -delete
# tar -cJvf 0ad-r8899.tar.xz 0ad-r8899

Name:           0ad
Version:        1.0
Release:        %mkrel 0.%{revision}.2
License:        GNU GPL v2 or later
Group:          Games/Strategy
Summary:        Cross-Platform RTS Game of Ancient Warfare
Url:            http://wildfiregames.com/0ad/
#Source:         0ad-r%{revision}.tar.xz
Source:		http://releases.wildfiregames.com/0ad-r%{revision}-alpha-unix-build.tar.xz
Requires:       0ad-data
BuildRequires:  boost-devel
BuildRequires:  devil-devel
BuildRequires:  fam-devel
BuildRequires:  gcc-c++
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libvorbis-devel
BuildRequires:  libxml2-devel
BuildRequires:  wxGTK-devel
BuildRequires:  wxgtku-devel
BuildRequires:  nasm
BuildRequires:  python
BuildRequires:  subversion
BuildRequires:  zip
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig
BuildRequires:  SDL-devel
BuildRequires:  wxGTK-devel
%ifarch x86_64
BuildRequires:	lib64xorg-x11-devel
%else
BuildRequires:	libxorg-x11-devel
%endif
BuildRequires:	libdnet-devel
#BuildRequires:	games-compat
%if %mdkversion <= 201010
BuildRequires: enet1.2-devel
%else
BuildRequires: enet-devel >= 1.3
%endif
BuildRequires:  openal-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}


%description
0 A.D. (pronounced "zero ey-dee") is a free, open-source, cross-platform
real-time strategy (RTS) game of ancient warfare. In short, it is a
historically-based war/economy game that allows players to relive or rewrite
the history of Western civilizations, focusing on the years between 500 B.C.
and 500 A.D. The project is highly ambitious, involving state-of-the-art 3D
graphics, detailed artwork, sound, and a flexible and powerful custom-built
game engine.

The game has been in development by Wildfire Games (WFG), a group of volunteer,
hobbyist game developers, since 2001.

#%package data
#Summary:        Data files for 0 A.D the RTS games
#Group:          Games/Strategy
#License:        GPLv2+ and CC-BY-SA
#BuildArch:      noarch
#Requires:       %{name} =  %{version}-%{release}

#%description data
#Data files for 0 A.D the RTS games such as sound, movies and images.

%prep
#%setup -q
%setup -q -n %{name}-r%{revision}-alpha
#cd %{name}-%{release}

%build
export CFLAGS="%{optflags}"
export CPPFLAGS="%{optflags}"
build/workspaces/update-workspaces.sh \
    --verbose \
    --bindir %{_bindir} \
    --datadir %{_datadir}/%{name} \
    --libdir %{_libdir}/%{name}
pushd build/workspaces/gcc
%make CONFIG=Release
popd

%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}/%{name}
./binaries/system/test -libdir binaries/system

%install
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 binaries/system/pyrogenesis %{buildroot}%{_bindir}/pyrogenesis
install -m 755 build/resources/0ad.sh %{buildroot}%{_bindir}/0ad

install -d -m 755 %{buildroot}%{_libdir}/%{name}
install -m 755 binaries/system/libCollada.so %{buildroot}%{_libdir}/%{name}/libCollada.so
install -m 755 binaries/system/libAtlasUI.so %{buildroot}%{_libdir}/%{name}/libAtlasUI.so
install -m 755 binaries/system/libmozjs-ps-release.so %{buildroot}%{_libdir}/%{name}/libmozjs-ps-release.so
install -m 755 binaries/system/libnvcore.so %{buildroot}%{_libdir}/%{name}/libnvcore.so
install -m 755 binaries/system/libnvimage.so %{buildroot}%{_libdir}/%{name}/libnvimage.so
install -m 755 binaries/system/libnvmath.so %{buildroot}%{_libdir}/%{name}/libnvmath.so
install -m 755 binaries/system/libnvtt.so %{buildroot}%{_libdir}/%{name}/libnvtt.so

install -d -m 755 %{buildroot}%{_datadir}/applications
install -m 644 build/resources/0ad.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop

install -d -m 755 %{buildroot}%{_datadir}/pixmaps
install -m 644 build/resources/0ad.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -a binaries/data/* %{buildroot}%{_datadir}/%{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README.txt LICENSE.txt
%doc license_gpl-2.0.txt license_lgpl-2.1.txt license_dbghelp.txt
%{_bindir}/0ad
%{_bindir}/pyrogenesis
%{_libdir}/%{name}
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}

#%files data
#%defattr(-,root,root)
#%{_datadir}/0ad
