#!/bin/sh
curl http://releases.wildfiregames.com/ 2>/dev/null |sed -e 's,</tr>,</tr>\n,g' |grep alpha-unix-build |tail -n1 |sed -e 's,-alpha-unix-build.*,,;s,.*0ad-,,'
