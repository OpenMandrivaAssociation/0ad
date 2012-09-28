# http://trac.wildfiregames.com/wiki/BuildInstructions#Linux

# conditionals left for the sake of users building from source, but
# nvtt (due to s3tc patented code) is not supported and not built.
%global		with_system_nvtt	0
%global		without_nvtt		1

%if 0%{?fedora} <= 16
%global		with_system_enet	0
%else
%global		with_system_enet	1
%endif

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
Version:        0.0.11
%if %mdkversion >= 201100
Release:        2
%else
Release:	%mkrel 2
%endif
# BSD License:
#	build/premake/*
#	libraries/valgrind/*		(not built/used)
# MIT License:
#	libraries/enet/*
#	libraries/fcollada/*
#	source/third_party/*
# LGPLv2+
#	libraries/cxxtest/*		(not built/used)
# GPLv2+
#	source/*
# IBM
#	source/tools/fontbuilder2/Packer.py
# MPL-1.1
#	libraries/spidermonkey/*	(not built/used)
License:	GPLv2+ and BSD and MIT and IBM
Group:          Games/Strategy
Summary:        Cross-Platform RTS Game of Ancient Warfare
Url:            http://wildfiregames.com/0ad/

%if %{without_nvtt}
# wget http://releases.wildfiregames.com/%%{name}-%%{version}-alpha-unix-build.tar.xz
# tar Jxf %%{name}-%%{version}-alpha-unix-build.tar.xz
# rm -fr %%{name}-%%{version}-alpha/libraries/nvtt
# rm -f %%{name}-%%{version}-alpha-unix-build.tar.xz
# tar Jcf %%{name}-%%{version}-alpha-unix-build.tar.xz %%{name}-%%{version}-alpha
Source0:	%{name}-%{version}-alpha-unix-build.tar.xz
%else
Source0:	http://releases.wildfiregames.com/%{name}-%{version}-alpha-unix-build.tar.xz
%endif

# adapted from binaries/system/readme.txt
# It is advisable to review this file at on newer versions, to update the
# version field and check for extra options. Note that windows specific,
# and disabled options were not added to the manual page.
Source1:	%{name}.6
Requires:	%{name}-data
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
%if %{with_system_nvtt}
BuildRequires:	nvidia-texture-tools
%endif
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

# FAMMonitorDirectory fails if passing a relative directory
# Use FAMNoExists (gamin specific to speed up a little bit initialization
# as commented in the source)
Patch0:		%{name}-gamin.patch

# http://trac.wildfiregames.com/ticket/1421
Patch1:		%{name}-rpath.patch

# Build with newer libxml2
Patch2:		%{name}-libxml2.patch

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
%patch1 -p1
%patch2 -p1

#-----------------------------------------------------------------------
%build
export CFLAGS="%{optflags}"
export CPPFLAGS="%{optflags}"
# avoid warnings with gcc 4.7 due to _FORTIFY_SOURCE in CPPFLAGS
export CPPFLAGS="`echo %{optflags} | sed -e 's/-Wp,-D_FORTIFY_SOURCE=2//'`"
build/workspaces/update-workspaces.sh	\
    --bindir %{_gamesbindir}		\
    --datadir %{_gamesdatadir}/%{name}	\
    --libdir %{_libdir}/%{name}		\
    --with-system-enet			\
    --with-system-mozjs185		\
%if %{with_system_nvtt}
    --with-system-nvtt			\
%endif
%if %{without_nvtt}
    --without-nvtt			\
%endif
    %{_smp_mflags}

%make -C build/workspaces/gcc config=%{config} verbose=1

#-----------------------------------------------------------------------
# Depends on availablity of nvtt
%if !%{without_nvtt}
%check
LD_LIBRARY_PATH=binaries/system binaries/system/test%{dbg} -libdir binaries/system
%endif

#-----------------------------------------------------------------------
%install
install -d -m 755 %{buildroot}%{_gamesbindir}
install -m 755 binaries/system/pyrogenesis%{dbg} %{buildroot}%{_gamesbindir}/pyrogenesis%{dbg}

install -d -m 755 %{buildroot}%{_libdir}/%{name}
for name in AtlasUI%{dbg} Collada%{dbg}; do
    install -m 755 binaries/system/lib${name}.so  %{buildroot}%{_libdir}/%{name}/lib${name}.so
done

%if !%{without_nvtt} && !%{with_system_nvtt}
for name in nvcore nvimage nvmath nvtt; do
    install -p -m 755 binaries/system/lib${name}.so %{buildroot}%{_libdir}/%{name}/lib${name}.so
done
%endif

install -d -m 755 %{buildroot}%{_gamesdatadir}/applications
install -m 644 build/resources/0ad.desktop %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop
perl -pi -e 's|%{_bindir}/0ad|%{_gamesbindir}/0ad|;'		\
    %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop    

install -d -m 755 %{buildroot}%{_gamesdatadir}/pixmaps
install -m 644 build/resources/0ad.png %{buildroot}%{_gamesdatadir}/pixmaps/%{name}.png

install -d -m 755 %{buildroot}%{_gamesdatadir}/%{name}
cp -a binaries/data/* %{buildroot}%{_gamesdatadir}/%{name}

install -d -m 755 %{buildroot}%{_mandir}/man6
install -p -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man6/%{name}.6
ln -sf %{name}.6 %{buildroot}%{_mandir}/man6/pyrogenesis.6

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
%{_mandir}/man6/*.6*
