#!/bin/bash
# This script was used to dump code. No changes needed.
# Keep it as is.
# If desired, you can remove or keep this script.

is_readable() {
    local file=$1
    local mime_type=$(file --mime-type -b "$file")

    if [[ $mime_type == text/* ]] || \
       [[ $file =~ \.(py|sh|txt|md|json|yaml|yml|cfg|conf|ini)$ ]]; then
        return 0
    else
        return 1
    fi
}

process_file() {
    local file=$1
    if [[ $file == *"/__pycache__/"* ]] || \
       [[ $file == */logs/* ]] || \
       [[ $file == */node_modules/* ]] || \
       [[ $file == */package-lock.json ]] || \
       [[ $file == */tensorboard_logs/* ]] || \
       [[ $file == */plotly_logs/* ]] || \
       [[ $file == */.git/* ]]; then
        return
    fi
    if [ -d "$file" ]; then
        for f in "$file"/*; do
            process_file "$f"
        done
    elif [ -f "$file" ]; then
        if is_readable "$file"; then
            echo "=== File: $file ==="
            echo "----------------------------------------"
            cat "$file"
            echo -e "\n----------------------------------------\n"
        fi
    fi
}

process_file "."


