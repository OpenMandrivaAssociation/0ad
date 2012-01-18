# http://trac.wildfiregames.com/wiki/BuildInstructions#Linux

%bcond_with	debug
%if %{with debug}
%define		config			debug
%define		dbg			_dbg
%undefine	_enable_debug_packages
%undefine	debug_package
%else
%define		config			release
%define		dbg			%{nil}
# 0ad-debug is useless if 0ad is stripped
# install gamin-debug to verify reason of patch0
%define		_enable_debug_packages	%{nil}
%define		debug_package		%{nil}
%endif

Name:           0ad
Epoch:		1
Version:        r10803
%if %mdkversion >= 201100
Release:        0.2
%else
Release:	%mkrel 0.2
%endif
License:        GPLv2+
Group:          Games/Strategy
Summary:        Cross-Platform RTS Game of Ancient Warfare
Url:            http://wildfiregames.com/0ad/
Source:		http://releases.wildfiregames.com/0ad-%{version}-alpha-unix-build.tar.xz
Requires:       0ad-data
BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  devil-devel
BuildRequires:  gamin-devel
BuildRequires:  gcc-c++
BuildRequires:	jpeg-devel
BuildRequires:	libdnet-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libvorbis-devel
BuildRequires:  libxml2-devel
BuildRequires:  nasm
BuildRequires:  pkgconfig
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(libenet)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libzip)
BuildRequires:	pkgconfig(mozjs185)
BuildRequires:	pkgconfig(openal)
BuildRequires:  python
BuildRequires:  SDL-devel
BuildRequires:  subversion
#BuildRequires:  wxGTK-devel
BuildRequires:  wxgtku-devel
BuildRequires:	X11-devel

# FAMMonitorDirectory fails if passing a relative directory
# Use FAMNoExists (gamin specific to speed up a little bit initialization
# as commented in the source)
Patch0:		0ad-r10803-gamin.patch

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

#-----------------------------------------------------------------------
%prep
%setup -q -n %{name}-%{version}-alpha

%patch0 -p1

#-----------------------------------------------------------------------
%build
export CFLAGS="%{optflags}"
export CPPFLAGS="%{optflags}"
build/workspaces/update-workspaces.sh	\
    --bindir %{_gamesbindir}		\
    --datadir %{_gamesdatadir}/%{name}	\
    --libdir %{_libdir}/%{name}		\
    --with-system-enet			\
    --with-system-mozjs185		\
    %{_smp_mflags}

%make -C build/workspaces/gcc config=%{config} verbose=1

#-----------------------------------------------------------------------
%check
LD_LIBRARY_PATH=binaries/system binaries/system/test%{dbg} -libdir binaries/system

#-----------------------------------------------------------------------
%install
install -d -m 755 %{buildroot}%{_gamesbindir}
install -m 755 binaries/system/pyrogenesis%{dbg} %{buildroot}%{_gamesbindir}/pyrogenesis%{dbg}

install -d -m 755 %{buildroot}%{_libdir}/%{name}
for name in AtlasUI%{dbg} Collada%{dbg} nvcore nvimage nvmath nvtt; do
    install -m 755 binaries/system/lib${name}.so  %{buildroot}%{_libdir}/%{name}/lib${name}.so
done

install -d -m 755 %{buildroot}%{_gamesdatadir}/applications
install -m 644 build/resources/0ad.desktop %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop

install -d -m 755 %{buildroot}%{_gamesdatadir}/pixmaps
install -m 644 build/resources/0ad.png %{buildroot}%{_gamesdatadir}/pixmaps/%{name}.png

install -d -m 755 %{buildroot}%{_gamesdatadir}/%{name}
cp -a binaries/data/* %{buildroot}%{_gamesdatadir}/%{name}

mkdir -p %{buildroot}%{_datadir}
mv -f %{buildroot}%{_gamesdatadir}/{pixmaps,applications} %{buildroot}%{_datadir}

cat > %{buildroot}%{_gamesbindir}/0ad <<EOF
#!/bin/sh

cd %{_gamesdatadir}/0ad
LD_LIBRARY_PATH=%{_libdir}/0ad %{_gamesbindir}/pyrogenesis%{dbg} "\$@"
EOF
chmod +x %{buildroot}%{_gamesbindir}/0ad

%if %{with debug}
export EXCLUDE_FROM_FULL_STRIP="libAtlasUI_dbg.so libCollada_dbg.so pyrogenesis_dbg"
%endif

#-----------------------------------------------------------------------
%files
%doc README.txt LICENSE.txt
%doc license_gpl-2.0.txt license_lgpl-2.1.txt license_dbghelp.txt
%{_gamesbindir}/0ad
%{_gamesbindir}/pyrogenesis%{dbg}
%{_libdir}/%{name}
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_gamesdatadir}/%{name}
