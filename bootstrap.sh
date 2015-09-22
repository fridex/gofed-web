#!/bin/bash

function printHelp {
	echo "$1 - A simple bootstrap sript for gofed-web"
	echo "Synopsis: $1 command [arg1 [arg2 ...]]"
	echo ""
	echo "command:"
	echo "	uglify		uglify Javascript files for deployment"
	echo "	debug		use unmangled files; suitable for development"
	echo ""
	echo "$VERSION"
}

function useUglify {
	echo 'Running uglifyjs on all JavaScript files'
	for file in `find ./static/goview/js/ -iname *.js \! -iname *.min.js`; do
		uglifyjs ${file} -o ${file%.*}.min.js
	done
}

function useDebug {
	echo 'Symlinking all JavaScript files for development'
	for file in `find ./static/goview/js/ -iname *.js \! -iname *.min.js`; do
		cp ${file} ${file%.*}.min.js
	done
}

case "$1" in
	"help")
		shift
		printHelp "${PROG}"
		exit 0
		;;
	"uglify")
		shift
		useUglify
		exit 0
		;;
	"debug")
		shift
		useDebug
		exit 0
		;;
	*)
		printHelp "${PROG}"
		exit 1
		;;
esac
