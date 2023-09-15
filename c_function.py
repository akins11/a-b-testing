from pandas import DataFrame, read_csv, NamedAgg
from numpy import where, mean, std

from plotly.express import line

from htmltools import tags
from faicons import icon_svg

from plotnine import (
    ggplot, aes, geom_density, labs, scale_y_continuous, theme_minimal, theme
)

days_map = {i : i[0:3] for i in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']}

hour_map = {
    0: "12 mid-night",
    **{i: f"{i} am" for i in range(12) if i != 0},
    12: "12 noon",
    **{i+12: f"{i} pm" for i in range(12) if i != 0}
}




def clean_data(df: DataFrame) -> DataFrame:

    f_df = df.drop(["Unnamed: 0"], axis=1)

    f_df["converted"] = f_df["converted"].apply(lambda x: 1 if x == True else 0)

    ordered_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    f_df["most ads day"] = f_df["most ads day"].astype("category")
    f_df["most ads day"] = f_df["most ads day"].cat.reorder_categories(ordered_days, ordered = True)

    f_df = f_df.rename(columns=lambda c: c.strip().replace(" ", "_"))

    f_df = f_df.rename(
        columns={
            "test_group": "group", 
            "total_ads": "total_views", 
            "most_ads_day": "most_views_day", 
            "most_ads_hour": "most_views_hour"
        }
    )

    return f_df


def clean_column_names(df: DataFrame) -> DataFrame:
     
     df.columns = df.columns.str.replace("_", " ").str.title().str.replace(" ", "_")

     return df


def extract_value(filtered_df: DataFrame, column: str):

    return filtered_df[column].values.tolist()[0]



def user_number_card(card_type: str, title_tag, value: int, percentage: float):

    if card_type != "all":
        percent_div = tags.div(
            tags.h4(f"{percentage}%", class_="text"), 

            tags.div(
                tags.div(class_=f"bar per-{round(percentage)} {card_type}"),

                class_="percentage-bar"
            ),

            class_="bottom"
        )

        icon = "flask-vial" if card_type == "test" else "users-gear"

    else:
        percent_div = tags.div(
            tags.h4(f"{percentage}%", class_="text"), 

            tags.div(
                tags.div(class_="bar per-100"),

                class_="percentage-bar"
            ),

            class_="bottom"
        )

        icon = "users-viewfinder"


    return tags.div(
        tags.div(
            title_tag,

            class_=f"top {card_type}"
        ),

        tags.div(
            tags.h3(f"{value:,}", class_="text"),
            tags.div(
                icon_svg(icon, height="2rem", margin_left="0", margin_right="0"),

                class_="icon-container"
            ),
            class_="middle"
        ),

        tags.div(class_="card-divider"),

        percent_div,

        class_=f"mt-user-count {card_type}"
    )



def conversion_card(card_type: str, title: str, value: int, percentage: float, rate: float):
    
    if card_type == "all":
        icon = "users-viewfinder"
    elif card_type == "test":
        icon = "flask-vial"
    else:
        icon = "users-gear"

    return tags.div(
        tags.div(
            tags.p(title),
            tags.div(
                icon_svg(icon, fill="#9C9C9C", height="1.5rem", margin_left="0", margin_right="0"),

                class_=f"icon-container {card_type}"
            ),

            class_="top"
        ),

        tags.div(
            tags.h3(f"{value:,}"),
            tags.h6(f"({percentage}%)", class_=f"percent {card_type}"),

            class_="middle",
        ),

        tags.div(
            tags.h4("Conversion Rate", class_="title"),

            tags.div(
                tags.div(class_=f"bar rate-{card_type}"),

                class_="percentage-bar"
            ),
            
            tags.h4(f"{rate}%", class_=f"bar-text {card_type}"),

            class_="bottom"
        ),

        class_=f"mt-conversion-container {card_type}"
    )



def group_views_count(df: DataFrame, group_column: str, group_value: str) -> DataFrame:

    f_df = (
        df
        .query(f"group == '{group_value}'")
        .groupby(group_column)
        .agg(
            number_users = NamedAgg(column=group_column, aggfunc="count"),
            total_converted = NamedAgg(column="converted", aggfunc="sum")
        )
        .reset_index()
        .assign(
            percentage = lambda _: round((_["number_users"] / _["number_users"].sum())*100, 2),
            conversion_rate = lambda _: round((_["total_converted"] / _["number_users"]) * 100, 3)
        )
    )
    
    return f_df[[group_column, "number_users", "percentage", "total_converted", "conversion_rate"]]



def plot_group_views_count(df: DataFrame, view_column: str, exp_group: str):

    f_df = df.copy()

    if exp_group == "test":
        title = "Ads"
        line_color = "#9e557a"

    else:
        title = "PSA"
        line_color = "#00BFB3"


    if view_column == "most_views_day":
        f_df["tooltip_label"] = f_df["most_views_day"]
        f_df["most_views_day"] = f_df["most_views_day"].replace(days_map)

        p_title = "Day"
        marker_size=10

    else:
        f_df["tooltip_label"] = f_df["most_views_hour"].replace(hour_map)
        p_title = "Hour"
        marker_size=6
        

    f_fig = line(
        data_frame=f_df,
        x=view_column,
        y="number_users",
        markers=True,
        title=f"The {p_title} Users Viewed the Highest Number of {title}", 
        labels={view_column: "", "number_users": "Number Of Users"},
        color_discrete_sequence=[line_color],
        hover_data=[view_column, "number_users", "tooltip_label", "percentage"]
    )

    min_value = f_df["number_users"].min()
    max_value = f_df["number_users"].max()

    mm_line_colors = []
    mm_point_colors = []

    for var in f_df["number_users"]:
        
        if min_value == var:
            mm_line_colors.append("#415A77")
            mm_point_colors.append("#415A77")
        elif max_value == var:
            mm_line_colors.append("#1B263B")
            mm_point_colors.append("#1B263B")
        else:
            mm_line_colors.append(line_color)
            mm_point_colors.append("#FFFFFF")


    f_fig.update_traces(
        line_width=2, 
        marker=dict(
            size=marker_size,
            color=mm_point_colors,
            line=dict(
                width=2,
                color=mm_line_colors
            )
        ),
        hovertemplate=f"{p_title} : <b>%{{customdata[0]}}</b><br>No. of Users: <b>%{{y:,}}</b><br>Percentage: %{{customdata[1]}}%",
        hoverlabel=dict(
            bgcolor=line_color,
            font_size=13,
            font=dict(color="#FFFFFF"),
            bordercolor="#FFFFFF"
        )
    )
    
    f_fig.show(config={"displayModeBar": False})



# Conversion Rate -----------------------------------------------------------
def plot_conversion_rate_views(df: DataFrame, view_column: str, exp_group: str):

    f_df = df.copy()
    
    if exp_group == "test":
        title = "Ads"
        line_color = "#9e557a"

    else:
        title = "PSA"
        line_color = "#00BFB3"


    if view_column == "most_views_day":
        f_df["tooltip_label"] = f_df["most_views_day"]
        f_df["most_views_day"] = f_df["most_views_day"].replace(days_map)

        p_title = "Day"
        xaxis_lab = ""
        marker_size=10

    else:
        f_df["tooltip_label"] = f_df["most_views_hour"].replace(hour_map)
        p_title = "Hour"
        xaxis_lab = "Hours"
        marker_size=6


    f_fig = line(
        data_frame=f_df,
        x=view_column,
        y="conversion_rate",
        markers=True,
        title=f"Rate of Conversion & {p_title} with the Highest Viewed {title}",
        labels={view_column: xaxis_lab, "conversion_rate": "Conversion Rate"},
        color_discrete_sequence=[line_color],
        hover_data=[view_column, "tooltip_label", "number_users", "total_converted"]
    )

    min_value = f_df["conversion_rate"].min()
    max_value = f_df["conversion_rate"].max()

    mm_line_colors = []
    mm_point_colors = []

    for var in f_df["conversion_rate"]:
        
        if min_value == var:
            mm_line_colors.append("#415A77")
            mm_point_colors.append("#415A77")
        elif max_value == var:
            mm_line_colors.append("#1B263B")
            mm_point_colors.append("#1B263B")
        else:
            mm_line_colors.append(line_color)
            mm_point_colors.append("#FFFFFF")

    f_fig.update_traces(
        line_width=2, 
        marker=dict(
            size=marker_size,
            color=mm_point_colors,
            line=dict(
                width=2,
                color=mm_line_colors
            )
        ),
        hovertemplate=f"{p_title} : <b>%{{customdata[0]}}</b><br>No. of Users : <b>%{{customdata[1]:,}}</b><br>No. of Converted : <b>%{{customdata[2]:,}}</b><br>Conversion Rate : <b>%{{y:,.2f}}%</b>",
        hoverlabel=dict(
            bgcolor=line_color,
            font_size=13,
            font=dict(color="#FFFFFF"),
            bordercolor="#FFFFFF"
        )
    )

    f_fig.update_layout(width=572)

    # if view_column == "most_views_hour":
    #     f_fig.update_xaxes(
    #         tickvals=list(range(24)),
    #         ticktext=[i for i in range(24)]
    #     )

    f_fig.show(config={"displayModeBar": False})




def mean_std(group_df: DataFrame) -> list:

    f_df = (
        group_df
        .groupby("group")["converted"]
        .agg([mean, std])
        .reset_index()
    )[["mean", "std"]]

    f_list = f_df.values.tolist()[0]

    return [round(s, 3) for s in f_list]



def plot_bootstrap_samples(df: DataFrame, group: str):

    if group == "ads_converted":
        title = "Test Group (Ads)"
        color = "#9e557a"
    else:
        title = "Control Group (PSA)"
        color = "#00BFB3"

    f_plt = (
        ggplot(df, aes(x=group)) +
        geom_density(color=color) +
        labs(
            x="conversion rate",
            y="Density",
            title=f"Density of Average Conversion for {title}"
        ) +
        scale_y_continuous(labels = lambda l: ["{:,.0f}".format(v) for v in l]) +
        theme_minimal() +
        theme(figure_size=(8, 5))
    ).draw()

    return f_plt




def info_card(p_tag, icon_name):

    return tags.div(
    tags.div(
        tags.div(tags.i(class_=f"bi bi-{icon_name}"), class_="icon-container"), #info-lg

        class_="top"
    ),

    tags.div(p_tag, class_="text"),

    class_="info-container"
)




def page_link(name: str, path: str, icon_class: str):

    return tags.div(
        tags.a(
            tags.i(class_=icon_class),
            tags.p(name, class_="text-decoration-underline"),
            href=path,
            class_="page-link"
        ),
        class_="link-container"
    )