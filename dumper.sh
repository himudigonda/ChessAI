#!/bin/bash

# Function to check if file is text/code
is_readable() {
    local file=$1
    local mime_type=$(file --mime-type -b "$file")
    
    # Check if it's a text file or common code file extension
    if [[ $mime_type == text/* ]] || \
       [[ $file =~ \.(py|sh|txt|md|json|yaml|yml|cfg|conf|ini)$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to process each file
process_file() {
    local file=$1
    
    # Skip if file is in ignored directories
    if [[ $file == *"/__pycache__/"* ]] || \
       [[ $file == */logs/* ]] || \
       [[ $file == */tensorboard_logs/* ]] || \
       [[ $file == */plotly_logs/* ]] || \
       [[ $file == */.git/* ]]; then
        return
    fi

    # If it's a directory, process its contents
    if [ -d "$file" ]; then
        for f in "$file"/*; do
            process_file "$f"
        done
    # If it's a file, check if it's readable and print contents
    elif [ -f "$file" ]; then
        if is_readable "$file"; then
            echo "=== File: $file ==="
            echo "----------------------------------------"
            cat "$file"
            echo -e "\n----------------------------------------\n"
        fi
    fi
}

# Start processing from current directory
process_file "."