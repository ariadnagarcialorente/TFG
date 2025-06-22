#!/bin/bash

# Activate environment
source ../env/bin/activate

# Logging helper with proper argument handling
run_and_log() {
  local label="$1"
  shift
  echo "Running: $label"
  echo "Command: $@"
  { time "$@" ; } 2>&1 | tee "logs_2/${label}.log"
}

# Ensure log directory exists
mkdir -p logs_2

# Simplified experiment parameters
ROWS=10000
COLS=1000

# Generate important columns list (first 100 columns)
IMPORTANT_COLS=""
for i in $(seq 1 100); do
  if [ $i -eq 1 ]; then
    IMPORTANT_COLS="col_$i"
  else
    IMPORTANT_COLS="$IMPORTANT_COLS,col_$i"
  fi
done

declare -A ALGO_COMMANDS=(
  ["v0.0"]="python algorithm_v0.0.py -r 9500 -p 90.0"
  ["v0.1"]="python algorithm_v0.1.py -r 9500 -p 90.0 -m 10000"
  ["v0.2"]="python algorithm_v0.2.py -p 75 -w 2.0"
  ["v0.3"]="python algorithm_v0.3.py -r 9500 -mp 90.0 -m 10000 -w 2.0"
  ["v0.4"]="python algorithm_v0.4.py -r 9500 -mp 90.0 -m 10000 -ct 800 -crt 80.0 -w 2.0 -sd 1.5"
  ["v0.5"]="python algorithm_v0.5.py -r 9500 -mp 90.0 -m 10000 -ct 800 -crt 80.0 -w 2.0"
  ["bnb"]="python branch_and_bound.py -r 9900 -l 900 -m 0.3 -w 2.0"  # CHANGED THIS LINE
)

# 10 Case definitions (simplified parameters)
CASE_TYPES=("MCAR" "MCAR" "MAR" "MAR" "MNAR" "MNAR" "Hybrid" "MCAR" "MAR" "MNAR")
CASE_PARAMS=(
  # Case 1: MCAR - Light missing (10%)
  "--num_columns 50 --percentage 10"
  
  # Case 2: MCAR - Heavy missing (25%) 
  "--num_columns 100 --percentage 25"
  
  # Case 3: MAR - Small dependency
  "--reference_column col_501 col_502 col_503 --target_column col_1 col_2 col_3 --cutoff 5000 5000 5000 --pi_high 0.3 0.3 0.3 --pi_low 0.1 0.1 0.1"
  
  # Case 4: MAR - Large dependency
  "--reference_column col_601 col_602 col_603 col_604 col_605 --target_column col_11 col_12 col_13 col_14 col_15 --cutoff 7500 7500 7500 7500 7500 --pi_high 0.6 0.6 0.6 0.6 0.6 --pi_low 0.2 0.2 0.2 0.2 0.2"
  
  # Case 5: MNAR - Moderate self-dependency
  "--column col_21 col_22 col_23 --cutoff 6000 6000 6000 --pi_high 0.4 0.4 0.4 --pi_low 0.15 0.15 0.15"
  
  # Case 6: MNAR - Strong self-dependency
  "--column col_31 col_32 col_33 col_34 col_35 --cutoff 8000 8000 8000 8000 8000 --pi_high 0.7 0.7 0.7 0.7 0.7 --pi_low 0.3 0.3 0.3 0.3 0.3"
  
  # Case 8: MCAR - Medium missing (15%)
  "--num_columns 75 --percentage 15"
  
  # Case 9: MAR - Complex dependency 
  "--reference_column col_701 col_702 col_703 col_704 --target_column col_41 col_42 col_43 col_44 --cutoff 6500 6500 6500 6500 --pi_high 0.5 0.5 0.5 0.5 --pi_low 0.25 0.25 0.25 0.25"
  
  # Case 10: MNAR - Complex self-dependency
  "--column col_51 col_52 col_53 col_54 --cutoff 7000 7000 7000 7000 --pi_high 0.6 0.6 0.6 0.6 --pi_low 0.2 0.2 0.2 0.2"
)

# Scale parameters based on simplified size
min_rows=$((ROWS / 2))           # 5000
max_missing=$((ROWS * COLS / 200))  # 50,000 (0.5% of total values)
col_threshold=$((COLS * 80 / 100))  # 800

echo "Starting experiments with $ROWS rows and $COLS columns"
echo "Important columns: first 100 columns"
echo "Scaled parameters: min_rows=$min_rows, max_missing=$max_missing, col_threshold=$col_threshold"

# Main experiment loop
for case_idx in "${!CASE_TYPES[@]}"; do
  CASE_TYPE=${CASE_TYPES[$case_idx]}
  PARAM=${CASE_PARAMS[$case_idx]}
  case_id="case$((case_idx+1))"
  complete_file="${case_id}_complete.csv"
  erased_file="${case_id}_erased.csv"

  echo "========================================="
  echo "Processing Case $((case_idx+1)): $CASE_TYPE"
  echo "========================================="

  # 1. Generate complete dataset
  echo "Step 1: Generating complete dataset..."
  run_and_log "${case_id}_generate" python dataset_generator_numerical.py \
    --rows "$ROWS" \
    --columns "$COLS" \
    --output "$complete_file"

  # Generate heatmap of original data
  run_and_log "${case_id}_heatmap_original" python heatmap.py \
    -i "$complete_file" \
    -o "logs_2/${case_id}_heatmap_original.png"

  # 2. Apply missingness based on case type
  echo "Step 2: Applying missingnes pattern ($CASE_TYPE)..."
  if [[ "$CASE_TYPE" == "MCAR" ]]; then
    run_and_log "${case_id}_mcar" python erase_generator_MCAR_GPU.py \
      -i "$complete_file" \
      -o "$erased_file" \
      $PARAM --gpu

  elif [[ "$CASE_TYPE" == "MAR" ]]; then
    run_and_log "${case_id}_mar" python erase_generator_MAR_GPU.py \
      -i "$complete_file" \
      -o "$erased_file" \
      $PARAM --gpu

  elif [[ "$CASE_TYPE" == "MNAR" ]]; then
    run_and_log "${case_id}_mnar" python erase_generator_MNAR_GPU.py \
      -i "$complete_file" \
      -o "$erased_file" \
      $PARAM --gpu
  fi

  # Generate heatmap of erased data
  run_and_log "${case_id}_heatmap_erased" python heatmap.py \
    -i "$erased_file" \
    -o "logs_2/${case_id}_heatmap_erased.png"

  # 3. Run all algorithms on this case
  echo "Step 3: Running all algorithms..."
  for algo in "${!ALGO_COMMANDS[@]}"; do
    echo "  Running algorithm: $algo"
    algo_cmd=${ALGO_COMMANDS[$algo]}
    cleaned_file="${case_id}_${algo}_cleaned.csv"
    log_label="${case_id}_${algo}"

    # Build command array
    cmd_parts=()
    IFS=' ' read -ra parts <<< "$algo_cmd"
    cmd_parts+=("${parts[@]}")
    
    # Add input/output parameters based on algorithm version
    if [[ $algo == "v0.0" || $algo == "v0.1" || $algo == "bnb" ]]; then
      cmd_parts+=(-i "$erased_file" -o "$cleaned_file")
    else
      cmd_parts+=(--input "$erased_file" --output "$cleaned_file")
    fi
    
    # Add important columns parameter
    cmd_parts+=(-c "$IMPORTANT_COLS")

    # Execute algorithm
    run_and_log "$log_label" "${cmd_parts[@]}"

    # Generate heatmap of cleaned data
    run_and_log "${log_label}_heatmap_cleaned" python heatmap.py \
      -i "$cleaned_file" \
      -o "logs_2/${log_label}_heatmap_cleaned.png"

    # Run evaluation
    echo "  Evaluating results for $algo..."
    run_and_log "${log_label}_eval" python final_analysis.py \
      --erased "$erased_file" \
      --cleaned "$cleaned_file" \
      --min-rows "$min_rows" \
      --min-percent 90.0 \
      --max-missing "$max_missing" \
      --col-threshold "$col_threshold" \
      --col-relative-threshold 80.0 \
      --important-cols "$IMPORTANT_COLS"
  done

  echo "Case $((case_idx+1)) completed successfully!"
  echo ""
done

echo "========================================="
echo "All experiments completed!"
echo "Check the logs_2/ directory for detailed results."
echo "========================================="