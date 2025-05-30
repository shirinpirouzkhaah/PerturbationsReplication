import pandas as pd
import os

types = [
    "IfElseCF", "ExceptionCF", "DeadCodeCF", "TryNcatchCF", "DataFlowCF",
    "EqualAssertCF", "NullAssertCF", "TrueFalseAssertCF", "IndependentSwapCF",
    "defUseBreakCF", "ShuffleNamesCF", "RandomNamesCF"
]

scenarios = ["org", "mitigation", "inline_comment", "CoT"]

for type_name in types:
    for scenario in scenarios:
        # Match casing in filenames
        file_scenario = scenario
        if scenario == "inline_comment":
            file_scenario = "Inline"
        elif scenario == "mitigation":
            file_scenario = "Mitigation"
        elif scenario == "org":
            file_scenario = "Org"
        elif scenario == "CoT":
            file_scenario = "CoT"

        filename = f"updated_df_{type_name}_{file_scenario}.csv"
        if not os.path.isfile(filename):
            continue

        df = pd.read_csv(filename)
        df_filtered = df[df["output"].notna()]
        total_valid = len(df_filtered)
        total_exact_match = (df_filtered["exact_match"] == 1).sum()
        percentage = (total_exact_match / total_valid * 100) if total_valid > 0 else 0

        print(f"{type_name} - {scenario}: {total_valid} & {total_exact_match} & {percentage:.2f}%")

