pacman::p_load("kableExtra", "ggplot2")

format_tab <- function(df, caption, ...) {
    tabela <- kable(
        df,
        caption = caption,
        booktabs = T,
        ...
    ) %>%
        kable_styling(
            latex_options = c("striped", "hold_position"),
            full_width = F
        )
    return(tabela)
}

style_surface <- function(plot, ...) {
    plot <- plot +
        theme(
            strip.background = element_rect(
                color = "black", fill = "lightblue", size = 0.5, linetype = "solid"
            ),
            strip.text.x = element_text(
                size = 10, color = "black",
            ),
            axis.line = element_line(colour = "black"),
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            panel.border = element_blank(),
            panel.background = element_blank(),
            ...
        )
    return(plot)
}