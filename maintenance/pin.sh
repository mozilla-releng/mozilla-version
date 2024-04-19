#!/usr/bin/env bash
set -ex

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_DIR="$(dirname -- "$SCRIPT_DIR")"

# XXX Can't use associative array because macOS ships bash 3
PYTHON_VERSION_WITH_REQUIREMENT_FILES=(
	'3.8 base test local'
	'3.11 docs'
)

for i in "${!PYTHON_VERSION_WITH_REQUIREMENT_FILES[@]}"; do
	python_version="$(echo "${PYTHON_VERSION_WITH_REQUIREMENT_FILES[$i]}" | cut -d' ' -f1)"
	read -ra requirement_files <<<$(echo "${PYTHON_VERSION_WITH_REQUIREMENT_FILES[$i]}" | cut -d' ' -f2-)
	read -ra requirement_paths <<<${requirement_files[*]/#/requirements/}
	read -ra requirement_paths <<<${requirement_paths[*]/%/.in}

	temp_dir="$(mktemp -d)"
	temp_requirement_dir="$temp_dir/requirements"
	mkdir -p "$temp_requirement_dir"

	cp ${requirement_paths[*]} "$temp_requirement_dir"
	PIP_COMMANDS="pip install pip-compile-multi && pip-compile-multi --allow-unsafe ${requirement_files[*]/#/--generate-hashes }"

	docker pull "python:$python_version"
	docker run \
		--tty \
		--rm \
		--volume "$temp_dir:/src" \
		--workdir /src \
		"python:$python_version" \
		bash -cx "$PIP_COMMANDS"

	cp "$temp_requirement_dir/"*".txt" "$REPO_DIR/requirements"
	rm -rf "$temp_dir"
done
