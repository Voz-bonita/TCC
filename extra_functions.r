pacman::p_load("kableExtra", "ggplot2", "magick")

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

coord_fixed_save_cropped <- function(plot, path) {
    ggplot2::ggsave(filename = path, plot = plot)
    img <- magick::image_read(path = path)
    info <- magick::image_info(img)
    img <- magick::image_crop(img, magick::geometry_area(
        info[["width"]],
        info[["height"]] - 392 - 350,
        x_off = 0, y_off = 350
    ))
    magick::image_write(img, path)
}