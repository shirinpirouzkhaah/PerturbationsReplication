import os
import pandas as pd
import re
from collections import defaultdict


root_dir = os.getcwd()
csv_path = os.path.join(root_dir, "Perturbations.csv")
maindf = pd.read_csv(csv_path)


selected_columns = [
    'source_code', 'review_comment', 'target',
    'DataTypeCFSource', 'DataTypeCFComment', 'DataTypeCFTarget',
    'IfElseCFSource', 'IfElseCFComment', 'IfElseCFTarget',
    'ExceptionCFSource', 'ExceptionCFComment', 'ExceptionCFTarget',
    'DeadCodeCFSource', 'DeadCodeCFComment', 'DeadCodeCFTarget',
    'TryNcatchCFSource', 'TryNcatchCFComment', 'TryNcatchCFTarget',
    'DataFlowCFSource', 'DataFlowCFComment', 'DataFlowCFTarget',
    'EqualAssertCFSource', 'EqualAssertCFComment', 'EqualAssertCFTarget',
    'NullAssertCFSource', 'NullAssertCFComment', 'NullAssertCFTarget',
    'TrueFalseAssertCFSource', 'TrueFalseAssertCFComment', 'TrueFalseAssertCFTarget',
    'ShuffleNamesCFSource', 'ShuffleNamesCFComment', 'ShuffleNamesCFTarget',
    'RandomNamesCFSource', 'RandomNamesCFComment', 'RandomNamesCFTarget',
    'IndependentSwapCFSource', 'IndependentSwapCFComment', 'IndependentSwapCFTarget',
    'defUseBreakCFSource', 'defUseBreakCFComment', 'defUseBreakCFTarget'
]
Results = maindf[selected_columns].copy()


gpt_df = pd.read_csv(os.path.join(".", "gpt-3.5-turbo", "OrgSourceCode_gpt-3.5-turbo.csv"))


gpt_selected = gpt_df[
    ['gpt-3.5-turbo_org_EXM',  
     'gpt-3.5-turbo_org_response',
     
     'gpt-3.5-turbo_mitigation_EXM',  
     'gpt-3.5-turbo_mitigation_response',
     
     'gpt-3.5-turbo_inline_comment_EXM', 
     'gpt-3.5-turbo_inline_comment_response',
     
     
     'gpt-3.5-turbo_CoT_EXM',
     'gpt-3.5-turbo_CoT_response'
     ]
]
Results = pd.concat([Results, gpt_selected], axis=1)
gpt_cols = [
    'gpt-3.5-turbo_org_EXM',  
    'gpt-3.5-turbo_org_response',
    'gpt-3.5-turbo_mitigation_EXM',  
    'gpt-3.5-turbo_mitigation_response',
    'gpt-3.5-turbo_inline_comment_EXM', 
    'gpt-3.5-turbo_inline_comment_response',
    'gpt-3.5-turbo_CoT_EXM',
    'gpt-3.5-turbo_CoT_response'
]


rename_map = {col: col.replace("gpt-3.5-turbo", "gpt-3.5-turbo_Source") for col in gpt_cols}
Results.rename(columns=rename_map, inplace=True)

# Adjust inline comment case in the column names
Results.rename(columns={
    'gpt-3.5-turbo_Source_inline_comment_EXM': 'gpt-3.5-turbo_Source_InlineComment_EXM',
    'gpt-3.5-turbo_Source_inline_comment_response': 'gpt-3.5-turbo_Source_InlineComment_response'
}, inplace=True)



print("Column names:", Results.columns.tolist())

#-------------------------------------------------------------------------------------------------------------

dir_path = os.path.join('.', 'gpt-3.5-turbo')
for filename in os.listdir(dir_path):
    if filename.endswith('.csv') and filename != 'OrgSourceCode_gpt-3.5-turbo.csv':
        CFtype = filename[len('gpt-3.5-turbo_'):-len('.csv')]  # Extract CF type
        CF_df = pd.read_csv(os.path.join(dir_path, filename))


        col_org = f"gpt-3.5-turbo_{CFtype}_EXM"
        col_orgnew = f"gpt-3.5-turbo_{CFtype}_org_EXM"
        col_mit = f"gpt-3.5-turbo_{CFtype}_mitigation_EXM"
        col_inl = f"gpt-3.5-turbo_{CFtype}_inline_EXM"
        col_inlnew = f"gpt-3.5-turbo_{CFtype}_InlineComment_EXM"
        col_cot = f"gpt-3.5-turbo_{CFtype}_CoT_EXM"
        
        Rcol_org = f"gpt-3.5-turbo_{CFtype}_response"
        Rcol_orgnew = f"gpt-3.5-turbo_{CFtype}_org_response"
        Rcol_mit = f"gpt-3.5-turbo_{CFtype}_mitigation_response"
        Rcol_inl = f"gpt-3.5-turbo_{CFtype}_inline_response"
        Rcol_inlnew = f"gpt-3.5-turbo_{CFtype}_InlineComment_response"
        Rcol_cot = f"gpt-3.5-turbo_{CFtype}_CoT_response"

        # Initialize new columns with NA
        new_cols_df = pd.DataFrame({
            col_orgnew: pd.NA,
            col_mit: pd.NA,
            col_inlnew: pd.NA,
            col_cot: pd.NA,
            Rcol_orgnew: pd.NA,
            Rcol_mit: pd.NA,
            Rcol_inlnew: pd.NA,
            Rcol_cot: pd.NA
            
        }, index=Results.index)
        

        Results = pd.concat([Results, new_cols_df], axis=1)


        CF_source_col = f"{CFtype}Source"


        for idx in Results.index:
            if pd.notna(Results.at[idx, CF_source_col]) and Results.at[idx, 'gpt-3.5-turbo_Source_org_EXM'] == True:
                Results.at[idx, col_orgnew] = CF_df.at[idx, col_org]
                Results.at[idx, col_mit] = CF_df.at[idx, col_mit]
                Results.at[idx, col_inlnew] = CF_df.at[idx, col_inl]
                Results.at[idx, col_cot] = CF_df.at[idx, col_cot]
                Results.at[idx, Rcol_orgnew] = CF_df.at[idx, Rcol_org]
                Results.at[idx, Rcol_mit] = CF_df.at[idx, Rcol_mit]
                Results.at[idx, Rcol_inlnew] = CF_df.at[idx, Rcol_inl]
                Results.at[idx, Rcol_cot] = CF_df.at[idx, Rcol_cot]





print("Column names:", Results.columns.tolist())
#-------------------------------------------------------------------------------------------------------------
def process_model(model_name, results_df):
    print(f"Processing model: {model_name}")
    
    model_dir = os.path.join('.', model_name)
    org_file = os.path.join(model_dir, f"OrgSourceCode_{model_name}.csv")
    org_df = pd.read_csv(org_file)

    org_cols = [
        f"{model_name}_org_EXM",
        f"{model_name}_mitigation_EXM",
        f"{model_name}_inline_comment_EXM",
        f"{model_name}_CoT_EXM",
        f"{model_name}_org_response",
        f"{model_name}_mitigation_response",
        f"{model_name}_inline_comment_response",
        f"{model_name}_CoT_response"
    ]

    results_df = pd.concat([results_df, org_df[org_cols]], axis=1)
    
    rename_map = {
        col: col.replace(f"{model_name}_", f"{model_name}_Source_")
        for col in org_cols
        if col in results_df.columns
    }
    
    results_df.rename(columns=rename_map, inplace=True)

    for filename in os.listdir(model_dir):
        if filename.endswith('.csv') and filename != f"OrgSourceCode_{model_name}.csv":
            CFtype = filename[len(f"{model_name}_"):-len('.csv')]
            cf_df = pd.read_csv(os.path.join(model_dir, filename))

            col_org = f"{model_name}_{CFtype}_EXM"
            col_orgnew = f"{model_name}_{CFtype}_org_EXM"
            col_mit = f"{model_name}_{CFtype}_mitigation_EXM"
            col_inl = f"{model_name}_{CFtype}_inline_EXM"
            col_inlnew = f"{model_name}_{CFtype}_InlineComment_EXM"
            col_cot = f"{model_name}_{CFtype}_CoT_EXM"
            
            Rcol_org = f"{model_name}_{CFtype}_response"
            Rcol_orgnew = f"{model_name}_{CFtype}_org_response"
            Rcol_mit = f"{model_name}_{CFtype}_mitigation_response"
            Rcol_inl = f"{model_name}_{CFtype}_inline_response"
            Rcol_inlnew = f"{model_name}_{CFtype}_InlineComment_response"
            Rcol_cot = f"{model_name}_{CFtype}_CoT_response"

            new_cols_df = pd.DataFrame({
                col_orgnew: pd.NA,
                col_mit: pd.NA,
                col_inlnew: pd.NA,
                col_cot: pd.NA,
                Rcol_orgnew: pd.NA,
                Rcol_mit: pd.NA,
                Rcol_inlnew: pd.NA,
                Rcol_cot: pd.NA
            }, index=results_df.index)

            results_df = pd.concat([results_df, new_cols_df], axis=1)

            source_col = f"{CFtype}Source"
            org_check_col = f"{model_name}_Source_org_EXM"

            for idx in results_df.index:
                if pd.notna(results_df.at[idx, source_col]) and results_df.at[idx, org_check_col] == True:
                    results_df.at[idx, col_orgnew] = cf_df.at[idx, col_org]
                    results_df.at[idx, col_mit] = cf_df.at[idx, col_mit]
                    results_df.at[idx, col_inlnew] = cf_df.at[idx, col_inl]
                    results_df.at[idx, col_cot] = cf_df.at[idx, col_cot]
                    results_df.at[idx, Rcol_orgnew] = cf_df.at[idx, Rcol_org]
                    results_df.at[idx, Rcol_mit] = cf_df.at[idx, Rcol_mit]
                    results_df.at[idx, Rcol_inlnew] = cf_df.at[idx, Rcol_inl]
                    results_df.at[idx, Rcol_cot] = cf_df.at[idx, Rcol_cot]

    return results_df



Results = process_model("Llama3.3_70B", Results)
Results = process_model("DeepSeek-V3", Results)



print("Column names:", Results.columns.tolist())

#-------------------------------------------------------------------------------------------------------------

def process_t5_model(results_df):
    print("Processing T5 model predictions...")

    t5_dir = os.path.join('.', 'T5')

    for filename in os.listdir(t5_dir):
        if filename.endswith('_predictions.csv'):
            print(f"Reading {filename}...")
            filepath = os.path.join(t5_dir, filename)
            df = pd.read_csv(filepath)
            core = filename[:-len('_predictions.csv')]
            CFtype, scenario = core.rsplit('_', 1)
            exm_col = f"exact_match_{CFtype}_{scenario}"
            pred_col = f"predictions_{CFtype}_{scenario}"
            dest_exm = f"T5_{CFtype}_{scenario}_EXM"
            dest_pred = f"T5_{CFtype}_{scenario}_pred"
            results_df[dest_exm] = pd.NA
            results_df[dest_pred] = pd.NA
            for i, row in df.iterrows():
                results_idx = row['index']
                if results_idx in results_df.index:
                    results_df.at[results_idx, dest_exm] = row[exm_col]
                    results_df.at[results_idx, dest_pred] = row[pred_col]
                
    return results_df

Results = process_t5_model(Results)
print("Column names:", Results.columns.tolist())



col_replacements = {
    "Mitigation": "CodeRepetition",
    "Inline": "InlineComment",
    "source": "Source"
}
new_columns = []
for col in Results.columns:
    if col.startswith("T5_"):
        new_col = col
        for old, new in col_replacements.items():
            new_col = new_col.replace(old, new)
        new_columns.append(new_col)
    else:
        new_columns.append(col)
        
Results.columns = new_columns

print("Column names:", Results.columns.tolist())


#-------------------------------------------------------------------------------------------------------------

def process_lora_model(results_df):
    print("Processing LoRaTunedLLaMa predictions...")

    lora_dir = os.path.join('.', 'LoRaTunedLLaMa')
    
    source_cols = {
        "Org": "LoRa_org",
        "Mitigation": "LoRa_mitigation",
        "Inline": "LoRa_inline_comment",
        "CoT": "LoRa_CoT"
    }
    
    for scenario, base_col_name in source_cols.items():
        file_name = f"updated_df_Source_{scenario}.csv"
        file_path = os.path.join(lora_dir, file_name)
        df = pd.read_csv(file_path)
    

        exm_col = f"{base_col_name}_EXM"
        pred_col = f"{base_col_name}_pred"
    
        results_df[exm_col] = df["exact_match"]
        results_df[pred_col] = df["predictions"]

        
        
    for filename in os.listdir(lora_dir):
        if filename.startswith("updated_df_") and filename.endswith(".csv") and "_Source_" not in filename:
            print(f"Reading {filename}...")
            core = filename[len("updated_df_"):-len(".csv")]
            CFtype, scenario = core.rsplit('_', 1)
    
            filepath = os.path.join(lora_dir, filename)
            df = pd.read_csv(filepath)
    
            dest_exm = f"LoRa_{CFtype}_{scenario}_EXM"
            dest_pred = f"LoRa_{CFtype}_{scenario}_pred"
    
            results_df[dest_exm] = pd.NA
            results_df[dest_pred] = pd.NA
    
            target_col = f"{CFtype}Target"
            org_check_col = "LoRa_org_EXM"
    
            output_to_exact = dict(zip(df["output"], df["exact_match"]))
            output_to_pred = dict(zip(df["output"], df["predictions"]))  
    
            for idx in results_df.index:
                target_val = results_df.at[idx, target_col]
                if (
                    pd.notna(target_val)
                    and target_val in output_to_exact
                    and results_df.at[idx, org_check_col] == True
                ):
                    results_df.at[idx, dest_exm] = output_to_exact[target_val]
                    results_df.at[idx, dest_pred] = output_to_pred[target_val]  


    return results_df


Results = process_lora_model(Results)
lora_cols = [
    'LoRa_org_EXM', 'LoRa_org_pred',
    'LoRa_mitigation_EXM', 'LoRa_mitigation_pred',
    'LoRa_inline_comment_EXM', 'LoRa_inline_comment_pred',
    'LoRa_CoT_EXM', 'LoRa_CoT_pred'
]

rename_map = {
    col: col.replace('LoRa', 'LoRa_Source', 1)
    for col in lora_cols if col in Results.columns
}

# Apply renaming
Results.rename(columns=rename_map, inplace=True)
lora_inline_rename_map = {
    col: col.replace("_Inline_", "_InlineComment_")
    for col in Results.columns
    if col.startswith("LoRa_") and "_Inline_" in col
}

Results.rename(columns=lora_inline_rename_map, inplace=True)
print("Column names:", Results.columns.tolist())

#-------------------------------------------------------------------------------------------------------------
for col in Results.columns:
    if col.endswith("_EXM"):
        Results[col] = Results[col].apply(
            lambda x: pd.NA if pd.isna(x)
            else True if x != 0
            else False
        )
        
print("Total columns:", len(Results.columns))
print("Column names:", Results.columns.tolist())
#-------------------------------------------------------------------------------------------------------------

scenario_map = {
    "org": "Org",
    "mitigation": "CodeRepetition",
    "inline": "InlineComment",
    "cot": "CoT"
}

cf_type_map = {
    "DataTypeCF": "DataType",
    "IfElseCF": "IfElseSwap",
    "ExceptionCF": "DeadException",
    "DeadCodeCF": "DeadVariable",
    "TryNcatchCF": "TryNcatchWrapper",
    "DataFlowCF": "ReturnViaVariable",
    "EqualAssertCF": "EqualAssert",
    "NullAssertCF": "NullAssert",
    "TrueFalseAssertCF": "TrueFalseAssert",
    "IndependentSwapCF": "IndependentLineSwap",
    "defUseBreakCF": "defUseBreak",
    "ShuffleNamesCF": "ShuffleNames",
    "RandomNamesCF": "RandomNames"
}

def clean_column_name(col):
    # Replace response with pred
    col = col.replace("response", "pred")

    # Normalize scenario
    for old, new in scenario_map.items():
        col = re.sub(rf"_{old}(?=(_pred|_EXM|$))", f"_{new}", col, flags=re.IGNORECASE)

    for old, new in cf_type_map.items():
        col = col.replace(old, new)

    return col



Results.columns = [clean_column_name(col) for col in Results.columns]
Results.columns = [col.replace("LoRa", "LLaMaLoRa") for col in Results.columns]

print("Total columns:", len(Results.columns))
print("Column names:", Results.columns.tolist())




#-------------------------------------------------------------------------------------------------------------
# Your model and scenario definitions
Models = ['T5', 'LLaMaLoRa', 'Llama3.3_70B', 'gpt-3.5-turbo', 'DeepSeek-V3']
Scenarios = ['Org', 'CoT', 'CodeRepetition', 'InlineComment']
BaseTypes = ["IfElseSwap", "EqualAssert", "NullAssert", "TrueFalseAssert", "DeadException", "DeadVariable", 
             "TryNcatchWrapper", "IndependentLineSwap", "ReturnViaVariable", 
             "defUseBreak", "DataType", "RandomNames", "ShuffleNames"]

# Mapping from raw CF_Type to printable names
TypePrintNames = {
    "IfElseSwap": "If else swap",
    "Assert wrapped in if statement": "Assert wrapped in if statement",
    "DeadException": "Dead Exception insertion",
    "DeadVariable": "Dead variable assignment insertion",
    "TryNcatchWrapper": "Try and catch wrapper",
    "IndependentLineSwap": "Independent line swap",
    "ReturnViaVariable": "Return via variable",
    "defUseBreak": "Def-use break",
    "DataType": "Data type",
    "RandomNames": "Random variable names",
    "ShuffleNames": "Shuffle variable names"
}

Results.columns = [col.replace("_inline_comment", "_InlineComment") for col in Results.columns]

print("\n=== DEBUG: Columns grouped by Model and Source ===\n")
for model in Models:
    print(f"\nModel: {model}")
    model_source_cols = [col for col in Results.columns if col.startswith(f"{model}_Source")]
    for col in sorted(model_source_cols):
        print(f"  - {col}")
#-------------------------------------------Save CSV------------------------------------------------------------------
output_filename = "Final_ACR_Evaluation_Results.csv"
Results.to_csv(output_filename, index=False)
print(f"Saved to {output_filename}")
#----------------------------------------------Original results + mitigations---------------------------------------------------------------
# Format map for scenario label
scenario_latex = {
    'Org': "Original input",
    'CoT': r'\quad + CoT',
    'CodeRepetition': r'\quad + Code Repetition',
    'InlineComment': r'\quad + Inline Comment'
}

# List of scenarios and models to include
Scenarios = ['Org', 'CoT', 'CodeRepetition', 'InlineComment']
Models = ['T5', 'LLaMaLoRa', 'Llama3.3_70B', 'gpt-3.5-turbo', 'DeepSeek-V3']

print("\n=== Source EXM Accuracy by Scenario ===\n")

for scenario in Scenarios:
    row = [scenario_latex[scenario]]
    for model in Models:
        if model == "T5":
            col_name = f"{model}_Source_{scenario}_EXM"
        else:
            col_name = f"{model}_Source_{scenario}_EXM"
        if col_name in Results.columns:
            total = Results[col_name].notna().sum()
            correct = Results[col_name].sum()
            percent = (correct / total * 100) if total > 0 else 0
            row.extend([str(total), str(correct), f"{percent:.2f}"])
        else:
            row.extend(["-", "-", "-"])
    print(" & ".join(row) + r" \\")
print(r"\midrule")


#-------------------------------------------------each ACR tool alone results------------------------------------------------------------

scenario_latex = {
    'Org': '',
    'CoT': r'\quad + CoT',
    'CodeRepetition': r'\quad + Code Repetition',
    'InlineComment': r'\quad + Inline Comment'
}

# Step 1: Compute per-model results with model-specific baseline

records = []
for model in Models:
    if model == "T5":
        baseline_rows = Results  # Use all rows for T5
    else:
        model_baseline_col = f"{model}_Source_Org_EXM"
        if model_baseline_col not in Results.columns:
            continue
        baseline_rows = Results[Results[model_baseline_col] == True]

    for cf_type in BaseTypes:
        for scenario in Scenarios:
            col_name = f"{model}_{cf_type}_{scenario}_EXM"
            if col_name in Results.columns:
                valid_mask = baseline_rows[col_name].notna()
                valid_count = valid_mask.sum()
                exm_count = baseline_rows.loc[valid_mask, col_name].sum()
                exm_percentage = (exm_count / valid_count) * 100 if valid_count > 0 else 0.0

                records.append({
                    'Model': model,
                    'CF_Type': cf_type,
                    'Scenario': scenario,
                    'Valid_Cases': valid_count,
                    'EXM_Count': exm_count,
                    'EXM_Percentage': round(exm_percentage, 2)
                })


# Step 2: Merge EqualAssert, NullAssert, TrueFalseAssert into "Assert wrapped in if statement"
merged_records = []
for model in Models:
    for scenario in Scenarios:
        subset = [r for r in records if r['Model'] == model and r['Scenario'] == scenario and r['CF_Type'] in {'EqualAssert', 'NullAssert', 'TrueFalseAssert'}]
        total_valid = sum(r['Valid_Cases'] for r in subset)
        total_exm = sum(r['EXM_Count'] for r in subset)
        percentage = (total_exm / total_valid) * 100 if total_valid > 0 else 0.0
        merged_records.append({
            'Model': model,
            'CF_Type': "Assert wrapped in if statement",
            'Scenario': scenario,
            'Valid_Cases': total_valid,
            'EXM_Count': total_exm,
            'EXM_Percentage': round(percentage, 2)
        })

# Remove old assert types and add merged
records = [r for r in records if r['CF_Type'] not in {'EqualAssert', 'NullAssert', 'TrueFalseAssert'}]
records.extend(merged_records)

# Step 3: Group for output
grouped = defaultdict(dict)
for rec in records:
    key = (rec['CF_Type'], rec['Scenario'])
    grouped[key][rec['Model']] = rec

# Step 4: Print LaTeX-formatted table rows
OutputTypes = [
    "IfElseSwap", "Assert wrapped in if statement", "DeadException", "DeadVariable",
    "TryNcatchWrapper", "IndependentLineSwap", "ReturnViaVariable", "defUseBreak",
    "DataType", "RandomNames", "ShuffleNames"
]

for cf_type in OutputTypes:
    for i, scenario in enumerate(Scenarios):
        key = (cf_type, scenario)
        row_parts = []

        if scenario == "Org":
            row_parts.append(TypePrintNames[cf_type])
        else:
            row_parts.append(scenario_latex[scenario])

        for model in Models:
            stats = grouped.get(key, {}).get(model, None)
            if stats:
                row_parts.extend([
                    str(stats['Valid_Cases']),
                    str(stats['EXM_Count']),
                    f"{stats['EXM_Percentage']:.2f}"
                ])
            else:
                row_parts.extend(["-", "-", "-"])

        print(" & ".join(row_parts) + r" \\")
    print(r"\midrule")



#--------------------------------------------All ACR tools resulst-----------------------------------------------------------------
# Step 1: Filter rows with non-NA values across all model Org columns
org_columns = [f"{model}_Source_Org_EXM" for model in Models[1:]]  # Skip T5 for 'Source'
baselineDF = Results[Results[org_columns].all(axis=1)].copy()


# Step 2: Aggregate stats into records
records = []
for model in Models:
    for cf_type in BaseTypes:
        for scenario in Scenarios:
            col_name = f"{model}_{cf_type}_{scenario}_EXM"
            if col_name in Results.columns:
                valid_mask = Results.loc[baselineDF.index, col_name].notna()
                valid_count = valid_mask.sum()
                exm_count = Results.loc[baselineDF.index[valid_mask], col_name].sum()
                exm_percentage = (exm_count / valid_count) * 100 if valid_count > 0 else 0.0
                records.append({
                    'Model': model,
                    'CF_Type': cf_type,
                    'Scenario': scenario,
                    'Valid_Cases': valid_count,
                    'EXM_Count': exm_count,
                    'EXM_Percentage': round(exm_percentage, 2)
                })


# Step 3: Merge assert types into one
merged_records = []
for scenario in Scenarios:
    for model in Models:
        subset = [r for r in records if r['Scenario'] == scenario and r['Model'] == model and r['CF_Type'] in {'EqualAssert', 'NullAssert', 'TrueFalseAssert'}]
        total_valid = sum(r['Valid_Cases'] for r in subset)
        total_exm = sum(r['EXM_Count'] for r in subset)
        percentage = (total_exm / total_valid) * 100 if total_valid > 0 else 0.0
        merged_records.append({
            'Model': model,
            'CF_Type': "Assert wrapped in if statement",
            'Scenario': scenario,
            'Valid_Cases': total_valid,
            'EXM_Count': total_exm,
            'EXM_Percentage': round(percentage, 2)
        })

# Add merged assert records and remove originals
records = [r for r in records if r['CF_Type'] not in {'EqualAssert', 'NullAssert', 'TrueFalseAssert'}]
records.extend(merged_records)

# Step 4: Group records for easy printing
grouped = defaultdict(dict)
for rec in records:
    key = (rec['CF_Type'], rec['Scenario'])
    grouped[key][rec['Model']] = rec

# Step 5: Final output formatting
OutputTypes = [
    "IfElseSwap", "Assert wrapped in if statement", "DeadException", "DeadVariable",
    "TryNcatchWrapper", "IndependentLineSwap", "ReturnViaVariable", "defUseBreak",
    "DataType", "RandomNames", "ShuffleNames"
]

scenario_latex = {
    'Org': '',
    'CoT': r'\quad + CoT',
    'CodeRepetition': r'\quad + Code Repetition',
    'InlineComment': r'\quad + Inline Comment'
}

for cf_type in OutputTypes:
    for i, scenario in enumerate(Scenarios):
        key = (cf_type, scenario)
        row_parts = []

        if scenario == "Org":
            # First line with full type name
            row_parts.append(TypePrintNames[cf_type])
        else:
            row_parts.append(scenario_latex[scenario])

        for model in Models:
            stats = grouped.get(key, {}).get(model, None)
            if stats:
                row_parts.extend([
                    str(stats['Valid_Cases']),
                    str(stats['EXM_Count']),
                    f"{stats['EXM_Percentage']:.2f}"
                ])
            else:
                row_parts.extend(["-", "-", "-"])

        print(" & ".join(row_parts) + r" \\")
    print(r"\midrule")

#-------------------------------------------------------------------------------------------------------------










