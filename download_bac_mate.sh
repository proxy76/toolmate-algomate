#!/usr/bin/env bash
#
# download_bac_mate.sh
# ---------------------
# Downloads every Mathematics Bacalaureat PDF (subiecte + bareme) from
# pro-matematica.ro for the years 2013 .. present, and sorts them into
# folders by specialization:
#
#   mate-info/           (M_mate-info)
#   stiintele-naturii/   (M_st-nat)
#   tehnologic/          (M_tehnologic)
#   pedagogic/           (M_pedagogic)
#
# Filenames already contain the year and session, so nothing collides.
# The script is idempotent: re-running it skips files already downloaded.
#
# Usage:
#   ./download_bac_mate.sh [output_dir]
#
# If no output_dir is given, files go into ./bac-matematica

set -euo pipefail

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
BASE_URL="https://www.pro-matematica.ro/bacalaureat"
START_YEAR=2013
END_YEAR="$(date +%Y)"          # "present"
OUTDIR="${1:-bac-matematica}"
SLEEP_BETWEEN=1                 # seconds between downloads (be polite to the server)
UA="Mozilla/5.0 (compatible; bac-downloader/1.0)"

# ----------------------------------------------------------------------
# Pick a downloader (curl or wget)
# ----------------------------------------------------------------------
if command -v curl >/dev/null 2>&1; then
    fetch_page() { curl -fsSL -A "$UA" "$1"; }
    fetch_file() { curl -fsSL -A "$UA" -o "$2" "$1"; }
elif command -v wget >/dev/null 2>&1; then
    fetch_page() { wget -qO- -U "$UA" "$1"; }
    fetch_file() { wget -q -U "$UA" -O "$2" "$1"; }
else
    echo "ERROR: neither curl nor wget is installed." >&2
    exit 1
fi

# ----------------------------------------------------------------------
# Map a PDF filename to its category folder
# ----------------------------------------------------------------------
category_for() {
    case "$1" in
        *M_mate-info*)   echo "mate-info" ;;
        *M_st-nat*)      echo "stiintele-naturii" ;;
        *M_tehnologic*)  echo "tehnologic" ;;
        *M_pedagogic*)   echo "pedagogic" ;;
        *)               echo "" ;;   # unknown -> skip
    esac
}

# ----------------------------------------------------------------------
# Prepare output folders
# ----------------------------------------------------------------------
mkdir -p "$OUTDIR"/{mate-info,stiintele-naturii,tehnologic,pedagogic}

total_downloaded=0
total_skipped=0
total_failed=0

echo "Downloading Bacalaureat Matematica PDFs ($START_YEAR .. $END_YEAR)"
echo "Output directory: $OUTDIR"
echo

# ----------------------------------------------------------------------
# Main loop: one page per year
# ----------------------------------------------------------------------
for year in $(seq "$START_YEAR" "$END_YEAR"); do
    page_url="$BASE_URL/$year.php"
    echo "=== $year ==="

    # Fetch the year page; if it doesn't exist yet (e.g. a future year), skip.
    html="$(fetch_page "$page_url" 2>/dev/null || true)"
    if [ -z "$html" ]; then
        echo "  (no page / empty — skipping)"
        echo
        continue
    fi

    # Extract every absolute PDF URL on the page, de-duplicated.
    mapfile -t urls < <(
        printf '%s\n' "$html" \
        | grep -oE 'https://www\.pro-matematica\.ro/bacalaureat/[0-9]{4}/[^"'"'"' ]+\.pdf' \
        | sort -u
    )

    if [ "${#urls[@]}" -eq 0 ]; then
        echo "  (no PDFs found)"
        echo
        continue
    fi

    for url in "${urls[@]}"; do
        fname="$(basename "$url")"
        cat="$(category_for "$fname")"

        if [ -z "$cat" ]; then
            echo "  ? uncategorized, skipping: $fname"
            continue
        fi

        dest="$OUTDIR/$cat/$fname"

        # Skip if we already have a non-empty copy.
        if [ -s "$dest" ]; then
            echo "  = exists:   $cat/$fname"
            total_skipped=$((total_skipped + 1))
            continue
        fi

        if fetch_file "$url" "$dest"; then
            echo "  + saved:    $cat/$fname"
            total_downloaded=$((total_downloaded + 1))
        else
            echo "  ! FAILED:   $url"
            rm -f "$dest"          # remove any partial file
            total_failed=$((total_failed + 1))
        fi

        sleep "$SLEEP_BETWEEN"
    done
    echo
done

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
echo "----------------------------------------"
echo "Done."
echo "  Downloaded: $total_downloaded"
echo "  Skipped (already present): $total_skipped"
echo "  Failed: $total_failed"
echo
echo "Files per category:"
for cat in mate-info stiintele-naturii tehnologic pedagogic; do
    count="$(find "$OUTDIR/$cat" -type f -name '*.pdf' 2>/dev/null | wc -l | tr -d ' ')"
    printf "  %-20s %s\n" "$cat" "$count"
done
