# ================================
# Install/load required libraries
# ================================
pkgs <- c("readxl", "dplyr", "ggplot2", "tidyr", "patchwork", "ggbreak", "rstudioapi")
installed <- pkgs %in% installed.packages()[,"Package"]
if (any(!installed)) install.packages(pkgs[!installed])
lapply(pkgs, library, character.only = TRUE)

# ================================
# Function to read and process file
# ================================
read_and_process <- function(filepath) {
  df <- readxl::read_excel(filepath, sheet = "Protein list")
  
  # Identify SpC and TIC columns
  spc_cols <- grep("^SpC", names(df), value = TRUE)
  tic_cols <- grep("^TIC", names(df), value = TRUE)
  
  # Convert to numeric
  df[spc_cols] <- lapply(df[spc_cols], as.numeric)
  df[tic_cols] <- lapply(df[tic_cols], as.numeric)
  
  # Compute averages
  df <- df %>%
    mutate(
      avg_SpC = rowMeans(select(., all_of(spc_cols)), na.rm = TRUE),
      avg_TIC = rowMeans(select(., all_of(tic_cols)), na.rm = TRUE)
    )
  return(df)
}

# ================================
# Select files
# ================================
cat("Select first file:\n")
file1 <- file.choose()
cat("Select second file:\n")
file2 <- file.choose()

df1 <- read_and_process(file1)
df2 <- read_and_process(file2)

cat("Number of proteins in File 1:", nrow(df1), "\n")
cat("Number of proteins in File 2:", nrow(df2), "\n")

label1 <- rstudioapi::showPrompt("File 1 Label", "Enter label for first file:")
label2 <- rstudioapi::showPrompt("File 2 Label", "Enter label for second file:")

# ================================
# Prepare violin plots
# ================================
plot_data <- bind_rows(
  df1 %>% mutate(Source = factor(label1, levels = c(label1, label2))),
  df2 %>% mutate(Source = factor(label2, levels = c(label1, label2)))
)

# SpC violin
p_spc <- ggplot(plot_data, aes(x = Source, y = avg_SpC, fill = Source)) +
  geom_violin(trim = FALSE) +
  theme_minimal() +
  labs(title = "Average SpC per Protein", y = "Average SpC", x = "")

# TIC violin
p_tic <- ggplot(plot_data, aes(x = Source, y = avg_TIC, fill = Source)) +
  geom_violin(trim = FALSE) +
  theme_minimal() +
  labs(title = "Average TIC per Protein", y = "Average TIC", x = "")

# ================================
# Volcano plot function for shared proteins
# ================================
make_volcano <- function(df1, df2, label1, label2) {
  shared_proteins <- intersect(df1$ProteinAC, df2$ProteinAC)
  df1_shared <- df1 %>% filter(ProteinAC %in% shared_proteins)
  df2_shared <- df2 %>% filter(ProteinAC %in% shared_proteins)
  
  spc_cols1 <- grep("^SpC", names(df1_shared), value = TRUE)
  spc_cols2 <- grep("^SpC", names(df2_shared), value = TRUE)
  tic_cols1 <- grep("^TIC", names(df1_shared), value = TRUE)
  tic_cols2 <- grep("^TIC", names(df2_shared), value = TRUE)
  
  volcano_df <- data.frame(ProteinAC = shared_proteins,
                           log2FC_SpC = NA_real_,
                           pvalue_SpC = NA_real_,
                           log2FC_TIC = NA_real_,
                           pvalue_TIC = NA_real_)
  
  for (i in seq_along(shared_proteins)) {
    prot <- shared_proteins[i]
    
    vals1_spc <- as.numeric(df1_shared[df1_shared$ProteinAC == prot, spc_cols1])
    vals2_spc <- as.numeric(df2_shared[df2_shared$ProteinAC == prot, spc_cols2])
    volcano_df$log2FC_SpC[i] <- log2(mean(vals2_spc, na.rm = TRUE) / mean(vals1_spc, na.rm = TRUE))
    volcano_df$pvalue_SpC[i] <- tryCatch(t.test(vals2_spc, vals1_spc)$p.value, error = function(e) NA)
    
    vals1_tic <- as.numeric(df1_shared[df1_shared$ProteinAC == prot, tic_cols1])
    vals2_tic <- as.numeric(df2_shared[df2_shared$ProteinAC == prot, tic_cols2])
    volcano_df$log2FC_TIC[i] <- log2(mean(vals2_tic, na.rm = TRUE) / mean(vals1_tic, na.rm = TRUE))
    volcano_df$pvalue_TIC[i] <- tryCatch(t.test(vals2_tic, vals1_tic)$p.value, error = function(e) NA)
  }
  
  # Add significance
  volcano_df <- volcano_df %>%
    mutate(sig_SpC = case_when(
      pvalue_SpC < 0.05 & log2FC_SpC > 0 ~ "Up in File2",
      pvalue_SpC < 0.05 & log2FC_SpC < 0 ~ "Down in File2",
      TRUE ~ "Not significant"
    ),
    sig_TIC = case_when(
      pvalue_TIC < 0.05 & log2FC_TIC > 0 ~ "Up in File2",
      pvalue_TIC < 0.05 & log2FC_TIC < 0 ~ "Down in File2",
      TRUE ~ "Not significant"
    ))
  
  # Volcano plots
  p_volcano_SpC <- ggplot(volcano_df, aes(x = log2FC_SpC, y = -log10(pvalue_SpC), color = sig_SpC)) +
    geom_point() +
    scale_color_manual(values = c("Up in File2" = "red",
                                  "Down in File2" = "green",
                                  "Not significant" = "gray")) +
    theme_minimal() +
    labs(title = "Volcano Plot (SpC) – Shared Proteins",
         x = paste0("log2 Fold Change (", label2, "/", label1, ")"),
         y = "-log10(p-value)", color = "Significance")
  
  p_volcano_TIC <- ggplot(volcano_df, aes(x = log2FC_TIC, y = -log10(pvalue_TIC), color = sig_TIC)) +
    geom_point() +
    scale_color_manual(values = c("Up in File2" = "red",
                                  "Down in File2" = "green",
                                  "Not significant" = "gray")) +
    theme_minimal() +
    labs(title = "Volcano Plot (TIC) – Shared Proteins",
         x = paste0("log2 Fold Change (", label2, "/", label1, ")"),
         y = "-log10(p-value)", color = "Significance")
  
  return(list(SpC = p_volcano_SpC, TIC = p_volcano_TIC))
}


# ================================
# Volcano plot for shared proteins
# ================================
shared_proteins <- intersect(df1$ProteinAC, df2$ProteinAC)
df1_shared <- df1 %>% filter(ProteinAC %in% shared_proteins)
df2_shared <- df2 %>% filter(ProteinAC %in% shared_proteins)

# Identify SpC and TIC columns
spc_cols1 <- grep("^SpC", names(df1_shared), value = TRUE)
spc_cols2 <- grep("^SpC", names(df2_shared), value = TRUE)
tic_cols1 <- grep("^TIC", names(df1_shared), value = TRUE)
tic_cols2 <- grep("^TIC", names(df2_shared), value = TRUE)

volcano_df <- df1_shared %>%
  select(ProteinAC) %>%
  left_join(df1_shared, by = "ProteinAC") %>%
  left_join(df2_shared, by = "ProteinAC", suffix = c("_1", "_2")) %>%
  rowwise() %>%
  mutate(
    log2FC_SpC  = log2(mean(c_across(all_of(spc_cols2))) / mean(c_across(all_of(spc_cols1)))),
    log2FC_TIC  = log2(mean(c_across(all_of(tic_cols2))) / mean(c_across(all_of(tic_cols1)))),
    pvalue_SpC  = tryCatch(wilcox.test(c_across(all_of(spc_cols2)), c_across(all_of(spc_cols1)))$p.value, error = function(e) NA),
    pvalue_TIC  = tryCatch(wilcox.test(c_across(all_of(tic_cols2)), c_across(all_of(tic_cols1)))$p.value, error = function(e) NA),
    sig_SpC = case_when(
      pvalue_SpC < 0.05 & log2FC_SpC > 0 ~ paste0("Up in ", label2),
      pvalue_SpC < 0.05 & log2FC_SpC < 0 ~ paste0("Down in ", label2),
      TRUE ~ "Not significant"
    ),
    sig_TIC = case_when(
      pvalue_TIC < 0.05 & log2FC_TIC > 0 ~ paste0("Up in ", label2),
      pvalue_TIC < 0.05 & log2FC_TIC < 0 ~ paste0("Down in ", label2),
      TRUE ~ "Not significant"
    )
  ) %>% ungroup()

# Volcano plots
p_volcano_SpC <- ggplot(volcano_df, aes(x = log2FC_SpC, y = -log10(pvalue_SpC), color = sig_SpC)) +
  geom_point() +
  scale_color_manual(values = c(
    paste0("Up in ", label2) = "red",
    paste0("Down in ", label2) = "green",
    "Not significant" = "gray"
  )) +
  theme_minimal() +
  labs(title = "Volcano Plot (SpC) – Shared Proteins",
       x = paste0("log2 Fold Change (", label2, "/", label1, ")"),
       y = "-log10(p-value)", color = "Significance")

p_volcano_TIC <- ggplot(volcano_df, aes(x = log2FC_TIC, y = -log10(pvalue_TIC), color = sig_TIC)) +
  geom_point() +
  scale_color_manual(values = c(
    paste0("Up in ", label2) = "red",
    paste0("Down in ", label2) = "green",
    "Not significant" = "gray"
  )) +
  theme_minimal() +
  labs(title = "Volcano Plot (TIC) – Shared Proteins",
       x = paste0("log2 Fold Change (", label2, "/", label1, ")"),
       y = "-log10(p-value)", color = "Significance")









# Generate volcano plots
volcano_plots <- make_volcano(df1, df2, label1, label2)

# ================================
# Display plots
# ================================
#(p_spc | p_tic) / (volcano_plots$SpC | volcano_plots$TIC)
p_spc + p_tic
volcano_plots$SpC
volcano_plots$TIC