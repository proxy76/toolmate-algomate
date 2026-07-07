#!/usr/bin/env bash
#
# Downloads ALL official BAC Matematica M_tehnologic (M2, filiera tehnologica)
# exam PDFs from pro-matematica.ro, for 2020-2026:
#   - Sesiunea I / II / speciala (official sessions) + Rezerva variants
#   - Simulare clasa a XII-a
#   - Model
#   - Teste (training test sets, available for 2020 and 2021 only on the source site)
#
# Usage:
#   chmod +x download_bac_m2_tehnologic.sh
#   ./download_bac_m2_tehnologic.sh
#
# Requires: curl, zip (both usually preinstalled on Mac/Linux;
#           on Windows use WSL or Git Bash)

set -e

ROOT="BAC_Matematica_M2_Tehnologic"
BASE="https://www.pro-matematica.ro/bacalaureat"

mkdir -p "$ROOT"

get () {
  # $1 = subfolder, $2 = filename (also used as URL suffix under $BASE/<year>/)
  local folder="$1"
  local year="$2"
  local fname="$3"
  mkdir -p "$ROOT/$folder"
  local out="$ROOT/$folder/$fname"
  if [ -s "$out" ]; then
    echo "skip (exists): $out"
    return
  fi
  echo "downloading: $fname"
  curl -sSL --fail -o "$out" "$BASE/$year/$fname" || echo "  !! FAILED: $fname"
}

########################################
# 2020
########################################
Y=2020
get "$Y/Sesiunea_I_24_iunie"        $Y "2020_E_c_Matematica_S1_M_tehnologic_Subiect_06_LRO.pdf"
get "$Y/Sesiunea_I_24_iunie"        $Y "2020_E_c_Matematica_S1_M_tehnologic_Barem_06_LRO.pdf"

get "$Y/Sesiunea_Speciala_7_iulie"  $Y "2020_E_c_Matematica_SS_M_tehnologic_Subiect_01_LRO.pdf"
get "$Y/Sesiunea_Speciala_7_iulie"  $Y "2020_E_c_Matematica_SS_M_tehnologic_Barem_01_LRO.pdf"

get "$Y/Sesiunea_II_25_august"      $Y "2020_E_c_Matematica_S2_M_tehnologic_Subiect_03_LRO.pdf"
get "$Y/Sesiunea_II_25_august"      $Y "2020_E_c_Matematica_S2_M_tehnologic_Barem_03_LRO.pdf"

get "$Y/Model"                      $Y "2020_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2020_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

for i in $(seq -w 1 20); do
  get "$Y/Teste" $Y "2020_E_c_matematica_M_tehnologic_Test_${i}.pdf"
  get "$Y/Teste" $Y "2020_E_c_matematica_M_tehnologic_Barem_${i}.pdf"
done

########################################
# 2021
########################################
Y=2021
get "$Y/Sesiunea_I_29_iunie"        $Y "2021_E_c_Matematica_S1_M_tehnologic_Subiect_02_LRO.pdf"
get "$Y/Sesiunea_I_29_iunie"        $Y "2021_E_c_Matematica_S1_M_tehnologic_Barem_02_LRO.pdf"

get "$Y/Sesiunea_I_Rezerva"         $Y "2021_E_c_Matematica_S1R_M_tehnologic_Subiect_01_LRO.pdf"
get "$Y/Sesiunea_I_Rezerva"         $Y "2021_E_c_Matematica_S1R_M_tehnologic_Barem_01_LRO.pdf"

get "$Y/Sesiunea_II_17_august"      $Y "2021_E_c_Matematica_S2_M_tehnologic_Subiect_04_LRO.pdf"
get "$Y/Sesiunea_II_17_august"      $Y "2021_E_c_Matematica_S2_M_tehnologic_Barem_04_LRO.pdf"

get "$Y/Simulare_XII_23_martie"     $Y "2021_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf"
get "$Y/Simulare_XII_23_martie"     $Y "2021_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Barem_LRO.pdf"

get "$Y/Model"                      $Y "2021_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2021_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

for i in $(seq -w 1 12); do
  get "$Y/Teste" $Y "2021_E_c_matematica_M_tehnologic_Test_${i}.pdf"
  get "$Y/Teste" $Y "2021_E_c_matematica_M_tehnologic_Barem_${i}.pdf"
done

########################################
# 2022 (no Teste sets published on the source site)
########################################
Y=2022
get "$Y/Sesiunea_I_21_iunie"        $Y "2022_E_c_Matematica_S1_M_tehnologic_Subiect_01_LRO.pdf"
get "$Y/Sesiunea_I_21_iunie"        $Y "2022_E_c_Matematica_S1_M_tehnologic_Barem_01_LRO.pdf"

get "$Y/Sesiunea_Speciala_19_mai"   $Y "2022_E_c_Matematica_SS_M_tehnologic_Subiect_03_LRO.pdf"
get "$Y/Sesiunea_Speciala_19_mai"   $Y "2022_E_c_Matematica_SS_M_tehnologic_Barem_03_LRO.pdf"

get "$Y/Sesiunea_II_17_august"      $Y "2022_E_c_Matematica_S2_M_tehnologic_Subiect_07_LRO.pdf"
get "$Y/Sesiunea_II_17_august"      $Y "2022_E_c_Matematica_S2_M_tehnologic_Barem_07_LRO.pdf"

get "$Y/Simulare_XII_29_martie"     $Y "2022_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf"
get "$Y/Simulare_XII_29_martie"     $Y "2022_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Barem_LRO.pdf"

get "$Y/Model"                      $Y "2022_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2022_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

########################################
# 2023
########################################
Y=2023
get "$Y/Sesiunea_I_27_iunie"        $Y "2023_E_c_Matematica_S1_M_tehnologic_Subiect_01_LRO.pdf"
get "$Y/Sesiunea_I_27_iunie"        $Y "2023_E_c_Matematica_S1_M_tehnologic_Barem_01_LRO.pdf"

get "$Y/Sesiunea_Speciala_16_mai"   $Y "2023_E_c_Matematica_SS_M_tehnologic_Subiect_06_LRO.pdf"
get "$Y/Sesiunea_Speciala_16_mai"   $Y "2023_E_c_Matematica_SS_M_tehnologic_Barem_06_LRO.pdf"

get "$Y/Sesiunea_II_17_august"      $Y "2023_E_c_Matematica_S2_M_tehnologic_Subiect_07_LRO.pdf"
get "$Y/Sesiunea_II_17_august"      $Y "2023_E_c_Matematica_S2_M_tehnologic_Barem_07_LRO.pdf"

get "$Y/Sesiunea_II_Rezerva"        $Y "2023_E_c_Matematica_S2R_M_tehnologic_Subiect_05_LRO.pdf"
get "$Y/Sesiunea_II_Rezerva"        $Y "2023_E_c_Matematica_S2R_M_tehnologic_Barem_05_LRO.pdf"

get "$Y/Simulare_XII_28_martie"     $Y "2023_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf"
get "$Y/Simulare_XII_28_martie"     $Y "2023_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Barem_LRO.pdf"

get "$Y/Model"                      $Y "2023_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2023_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

########################################
# 2024
########################################
Y=2024
get "$Y/Sesiunea_I_2_iulie"         $Y "2024_E_c_Matematica_S1_M_tehnologic_Subiect_10_LRO.pdf"
get "$Y/Sesiunea_I_2_iulie"         $Y "2024_E_c_Matematica_S1_M_tehnologic_Barem_10_LRO.pdf"

get "$Y/Sesiunea_Speciala_22_mai"   $Y "2024_E_c_Matematica_SS_M_tehnologic_Subiect_09_LRO.pdf"
get "$Y/Sesiunea_Speciala_22_mai"   $Y "2024_E_c_Matematica_SS_M_tehnologic_Barem_09_LRO.pdf"

get "$Y/Sesiunea_II_20_august"      $Y "2024_E_c_Matematica_S2_M_tehnologic_Subiect_03_LRO.pdf"
get "$Y/Sesiunea_II_20_august"      $Y "2024_E_c_Matematica_S2_M_tehnologic_Barem_03_LRO.pdf"

get "$Y/Sesiunea_II_Rezerva"        $Y "2024_E_c_Matematica_S2R_M_tehnologic_Subiect_01_LRO.pdf"
get "$Y/Sesiunea_II_Rezerva"        $Y "2024_E_c_Matematica_S2R_M_tehnologic_Barem_01_LRO.pdf"

get "$Y/Simulare_XII_5_martie"      $Y "2024_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf"
get "$Y/Simulare_XII_5_martie"      $Y "2024_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Barem_LRO.pdf"

get "$Y/Model"                      $Y "2024_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2024_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

########################################
# 2025
########################################
Y=2025
get "$Y/Sesiunea_I_11_iunie"        $Y "2025_E_c_Matematica_S1_M_tehnologic_Subiect_01_LRO.pdf"
get "$Y/Sesiunea_I_11_iunie"        $Y "2025_E_c_Matematica_S1_M_tehnologic_Barem_01_LRO.pdf"

get "$Y/Sesiunea_Speciala_23_mai"   $Y "2025_E_c_Matematica_SS_M_tehnologic_Subiect_03_LRO.pdf"
get "$Y/Sesiunea_Speciala_23_mai"   $Y "2025_E_c_Matematica_SS_M_tehnologic_Barem_03_LRO.pdf"

get "$Y/Sesiunea_II_12_august"      $Y "2025_E_c_Matematica_S2_M_tehnologic_Subiect_09_LRO.pdf"
get "$Y/Sesiunea_II_12_august"      $Y "2025_E_c_Matematica_S2_M_tehnologic_Barem_09_LRO.pdf"

get "$Y/Simulare_XII_25_martie"     $Y "2025_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf"
get "$Y/Simulare_XII_25_martie"     $Y "2025_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Barem_LRO.pdf"

get "$Y/Model"                      $Y "2025_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2025_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

########################################
# 2026
########################################
Y=2026
get "$Y/Sesiunea_I_1_iulie"         $Y "2026_E_c_Matematica_S1_M_tehnologic_Subiect_03_LRO.pdf"
get "$Y/Sesiunea_I_1_iulie"         $Y "2026_E_c_Matematica_S1_M_tehnologic_Barem_03_LRO.pdf"

get "$Y/Sesiunea_I_Rezerva"         $Y "2026_E_c_Matematica_S1R_M_tehnologic_Subiect_07_LRO.pdf"
get "$Y/Sesiunea_I_Rezerva"         $Y "2026_E_c_Matematica_S1R_M_tehnologic_Barem_07_LRO.pdf"

get "$Y/Sesiunea_Speciala_19_mai"   $Y "2026_E_c_Matematica_SS_M_tehnologic_Subiect_02_LRO.pdf"
get "$Y/Sesiunea_Speciala_19_mai"   $Y "2026_E_c_Matematica_SS_M_tehnologic_Barem_02_LRO.pdf"

get "$Y/Simulare_XII_24_martie"     $Y "2026_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Subiect_LRO.pdf"
get "$Y/Simulare_XII_24_martie"     $Y "2026_E_c_Matematica_SM_M_tehnologic_Simulare_XII_Barem_LRO.pdf"

get "$Y/Model"                      $Y "2026_E_c_Matematica_SM_M_tehnologic_Model_Subiect_LRO.pdf"
get "$Y/Model"                      $Y "2026_E_c_Matematica_SM_M_tehnologic_Model_Barem_LRO.pdf"

########################################
# Zip everything up
########################################
ZIPNAME="BAC_Matematica_M2_Tehnologic_2020-2026.zip"
rm -f "$ZIPNAME"
zip -r -q "$ZIPNAME" "$ROOT"
echo ""
echo "Done. Created $ZIPNAME"
echo "(Any failed downloads are logged above as '!! FAILED' - re-run the script to retry, already-downloaded files are skipped.)"
