#!/bin/bash
# vim: set noet sw=4 ts=4 :
set -o nounset
set -o errexit

script_dir="${BASH_SOURCE%/*}"
if [[ ! -d "$script_dir" ]]; then
	script_dir="$PWD"
fi
source "$script_dir/config.sh"

version=$(git describe --dirty --always)
plain_version=${version#v}

die_with_usage() {
	echo "Usage: $0 [--save-local]" 1>&2
	exit 1
}

push_image=
save_local=
do_build=t
while [ $# -gt 0 ]; do
	case "$1" in
		--push)
			push_image=t
			;;
		--push-only)
			do_build=
			;;
		--registry*)
			container_registry="${1#--registry=}"
			;;
		--save-local)
			save_local=t
			;;
		*)
			echo "Error unknown option $1" 1>&2
			die_with_usage
			;;
	esac
	shift
done

build_container()  {
	bash "$script_dir/bin/docker_build_context.sh"
	docker build --tag=$container_name:$plain_version build/docker \
		--build-arg VERSION=$version
	docker tag $container_name:$plain_version $container_name:latest
}

save_local() {
	outfile="$container_name-$plain_version.docker.tgz"
	docker save $container_name:$plain_version | gzip >$script_dir/../$outfile
	echo "Docker image saved as '../$outfile'"
}

push_image() {
    target=$container_registry/$container_registry_path/$container_name
    docker tag $container_name:$plain_version $target:$plain_version
    docker tag $container_name:$plain_version $target:latest
    docker push $target:$plain_version
    docker push $target:latest
    echo "Pushed '$target:$plain_version'"
}

build_container
if [ "$save_local" ]; then
	save_local
fi
if [ "$push_image" ]; then
	push_image
fi
