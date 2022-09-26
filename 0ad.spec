# http://trac.wildfiregames.com/wiki/BuildInstructions#Linux

# enable special maintainer debug build ?
%define with_debug 0
%if %{with_debug}
%define config debug
%define dbg _dbg
%else
%define config release
%define dbg %{nil}
%endif

%global with_system_nvtt 0
%global with_system_mozjs 1

%global without_nvtt 1

Name:		0ad
Epoch:		1
Version:	0.0.26
Release:	1
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
Group:		Games/Strategy
Summary:	Cross-Platform RTS Game of Ancient Warfare
Url:		http://play0ad.com

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
BuildRequires:	rustc
BuildRequires:	cargo
BuildRequires:	desktop-file-utils
BuildRequires:	subversion
#BuildRequires:	devil-devel
#BuildRequires:	gamin-devel
BuildRequires:	icu-devel
BuildRequires:	libdnet-devel
BuildRequires:	nasm
%if %{with_system_nvtt}
BuildRequires:	nvidia-texture-tools-devel
%endif
BuildRequires:	boost-devel
BuildRequires:	cmake
BuildRequires:	pkgconfig(egl)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(dri)
BuildRequires:	egl-devel
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	miniupnpc-devel
BuildRequires:	pkgconfig(IL)
BuildRequires:	pkgconfig(libzip)
%if %with_system_mozjs
BuildRequires:	pkgconfig(mozjs-78)
%endif
BuildRequires:	pkgconfig(libidn)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(libcrypto)
BuildRequires:	pkgconfig(fmt)
BuildRequires:	pkgconfig(gloox)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(libenet)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(openal)
BuildRequires:	pkgconfig(sdl2)
BuildRequires:	pkgconfig(valgrind)
BuildRequires:	pkgconfig(vorbisfile)
BuildRequires:	pkgconfig(xcursor)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libsodium)
BuildRequires:	pkgconfig(freetype2)
# FIXME as 0f 0.23 and wxwidgets 3.1.5, if we use WxQt, the scenario editor
# crashes on startup due to widget parenting issues.
# Try again when new versions are released. In the mean time, WxGTK will have
# to do.
BuildRequires:	wxgtku3.2-devel

# Adding include directories in the wrong order the way 0ad likes to do
# results in cstdlib not finding stdlib.h with include_next
Patch5:			0ad-0.0.23-dont-mess-with-include-dirs.patch

# Fix build with zlib-ng
Patch11:			0ad-no-ZEXPORT.patch

Patch12:			https://src.fedoraproject.org/rpms/0ad/raw/rawhide/f/Fixup-compatibility-of-mozbuild-with-Python-3.10.patch
Patch13:			0ad-allow-mozjs-78.15.patch
#Patch14:			0ad-25b-compile.patch
#Patch15:			https://code.wildfiregames.com/file/data/qxiyxomtpjjypcmnsqus/PHID-FILE-cgwijqmkik4muyj3fjlg/D4669.diff
Patch16:			https://src.fedoraproject.org/rpms/0ad/raw/rawhide/f/0ad-debug.patch

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
%autosetup -p1 -n %{name}-%{version}-alpha

%if %{with_system_nvtt}
rm -fr libraries/nvtt
%endif

sed -i 's/"0"/"-1"/' build/workspaces/update-workspaces.sh
#sed -i 's/@ar/binutils-ar/' libraries/source/fcollada/src/Makefile

build/workspaces/clean-workspaces.sh

#-----------------------------------------------------------------------
%build
%set_build_flags
export CFLAGS="%{optflags}"
#export AR=binutils-ar
# avoid warnings with gcc 4.7 due to _FORTIFY_SOURCE in CPPFLAGS
export CPPFLAGS="$(echo %{optflags} | sed -e 's/-Wp,-D_FORTIFY_SOURCE=2//')"

build/workspaces/update-workspaces.sh	\
	--bindir=%{_gamesbindir}	\
	--datadir=%{_gamesdatadir}/%{name} \
	--libdir=%{_libdir}/%{name}	\
	--without-pch			\
%if %{with_system_mozjs}
	--with-system-mozjs		\
%endif
%if %{with_system_nvtt}
	--with-system-nvtt		\
%endif
%if %{without_nvtt}
	--without-nvtt			\
%endif
	%{?_smp_mflags}

# 0ad does some very very very weird stuff to compiler flags...
sed -i -e "s,-isystem.*,-I`pwd`/libraries/source/cxxtest-4.4 -I%{_includedir}/SDL2 -I%{_includedir}/X11 -I%{_includedir}/valgrind -I`pwd`/libraries/source/spidermonkey/include-unix-release -I`pwd`/source/third_party/tinygettext/include -I%{_includedir}/libxml2 -I%{_includedir}/wx-3.2 -I%{_libdir}/wx/include/gtk3-unicode-3.2 -I`pwd`/libraries/source/fcollada/include -I%{_includedir}/mozjs-78 -I`pwd`/libraries/source/glad/include -isystem %{_includedir}/freetype2,g" build/workspaces/gcc/*.make

%make_build -C build/workspaces/gcc config=%{config} verbose=1

#-----------------------------------------------------------------------
# Depends on availablity of nvtt
%if !%{without_nvtt}
%check
#LD_LIBRARY_PATH=binaries/system binaries/system/test%{dbg}
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

%if ! %{with_system_mozjs}
install -p -m 755 binaries/system/libmozjs78-ps-release.so %{buildroot}%{_libdir}/%{name}/
%endif

install -d -m 755 %{buildroot}%{_datadir}/appdata
install -p -m 644 build/resources/0ad.appdata.xml %{buildroot}%{_datadir}/appdata

install -d -m 755 %{buildroot}%{_gamesdatadir}/applications
install -m 644 build/resources/0ad.desktop %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop
perl -pi -e 's|%{_bindir}/0ad|%{_gamesbindir}/0ad|;' \
    %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop

install -d -m 755 %{buildroot}%{_gamesdatadir}/pixmaps
install -m 644 build/resources/0ad.png %{buildroot}%{_gamesdatadir}/pixmaps/%{name}.png

install -d -m 755 %{buildroot}%{_gamesdatadir}/%{name}
cp -a binaries/data/* %{buildroot}%{_gamesdatadir}/%{name}

install -d -m 755 %{buildroot}%{_mandir}/man6
install -p -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man6/%{name}.6
ln -sf %{name}.6 %{buildroot}%{_mandir}/man6/pyrogenesis.6

desktop-file-validate %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop

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
%doc license_gpl-2.0.txt license_lgpl-2.1.txt
%{_gamesbindir}/0ad
%{_gamesbindir}/pyrogenesis%{dbg}
%{_libdir}/%{name}
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/appdata/0ad.appdata.xml
%{_datadir}/applications/%{name}.desktop
%{_gamesdatadir}/%{name}
%{_mandir}/man6/*.6*

# Disable broken debug file on ARM
%ifarch %{arm} %{amrx}
%exclude %{_prefix}/lib/debug/core.19798
%endif
