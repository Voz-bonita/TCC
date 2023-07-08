pacman::p_load("jsonlite", "dplyr", "ggplot2", "purrr")

data <- read_json("./scrapping/info_all.json")
source("extra_functions.r", encoding = "UTF-8")

expectation <- function(variable, vals, df, moment = 1) {
    expect_variable <- (vals^moment * map_dbl(vals, ~
        filter_at(df, vars(variable), any_vars(. == .x)) %>%
            pull(Proporção) %>%
            sum())) %>%
        sum()
    return(expect_variable)
}

x <- 0:5
y <- 0:5
size <- length(x) * length(y)
score_df <- expand.grid(x, y) %>%
    cbind(., rep(0, size)) %>%
    cbind(., rep(names(data), each = size)) %>%
    rename_all(~ c("x", "y", "Proporção", "liga"))
n_leagues <- length(data)
corr_test_df <- data.frame(matrix(ncol = 5, nrow = n_leagues)) %>%
    rename_all(~ c(
        "Liga", "n", "r",
        "Estatística", "p-valor"
    ))

for (league_index in 1:n_leagues) {
    league <- names(data)[league_index]
    n_max <- length(data[[league]])
    for (game in names(data[[league]])) {
        info <- data[[league]][[game]]
        home <- min(info[["home_score"]], 5)
        away <- min(info[["away_score"]], 5)
        index <- (home + 6 * away + 1) + (league_index - 1) * size
        score_df[index, "Proporção"] <- score_df[index, "Proporção"] + 1 / n_max
    }

    score_xy <- filter(score_df, liga == league) %>%
        mutate("xy" = x * y)
    all_xy <- unique(score_xy[["xy"]])
    exy <- expectation(variable = "xy", vals = all_xy, df = score_xy)
    ex <- expectation(variable = "x", vals = x, df = score_xy)
    ex2 <- expectation(variable = "x", vals = x, df = score_xy, moment = 2)
    ey <- expectation(variable = "y", vals = y, df = score_xy)
    ey2 <- expectation(variable = "y", vals = y, df = score_xy, moment = 2)
    varx <- ex2 - ex^2
    vary <- ey2 - ey^2
    corr <- (exy - ex * ey) / sqrt(varx) / sqrt(vary)
    tstar <- corr * sqrt(n_max - 2) / sqrt(1 - corr^2)
    p_val <- 2 * pt(abs(tstar), df = n_max - 2, lower.tail = F)

    corr_test_df[league_index, "Liga"] <- league
    corr_test_df[league_index, "n"] <- n_max
    corr_test_df[league_index, "r"] <- corr
    corr_test_df[league_index, "Estatística"] <- tstar
    corr_test_df[league_index, "p-valor"] <- p_val
}

corr_test_df["n"] <- as.numeric(corr_test_df["n"])
corr_test_df["r"] <- as.numeric(corr_test_df["r"])
corr_test_df["Estatística"] <- as.numeric(corr_test_df["Estatística"])
corr_test_df["p-valor"] <- as.numeric(corr_test_df["p-valor"])
temp <- round(corr_test_df[["p-valor"]], 3)
corr_test_df["p-valor"] <- ifelse(temp < 0.1, ifelse(temp < 0.001, "$<$ 0.001", temp), "$>$ 0.1")
corr_test_df %>%
    na.omit() %>%
    format_tab(
        "\\label{tab:corr_test}Resultados dos testes de ausência de correlação entre os gols do time da casa e do time visitante",
        digits = 3, format = "latex"
    )

(ggplot(
    data = filter(score_df, liga != "Supercopa do Brasil"),
    aes(x = `x`, y = `y`, fill = `Proporção`)
) +
    geom_tile(color = "black", lwd = 0.5) +
    facet_wrap(vars(liga), ncol = 6) +
    xlab("Gols do time da casa") +
    ylab("Gols to time visitante") +
    scale_x_continuous(breaks = 0:5) +
    scale_y_continuous(breaks = 0:5) +
    scale_fill_gradient(low = "#5a5151", high = "orange")) %>%
    style_surface(legend.position = "bottom") %>%
    coord_fixed_save_cropped(
        path = "assets/gols_prop.png",
        offset_up = 0, offset_down = 0
    )