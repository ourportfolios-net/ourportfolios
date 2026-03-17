import reflex as rx

config = rx.Config(
    app_name="ourportfolios",
    plugins=[rx.plugins.TailwindV3Plugin(), rx.plugins.sitemap.SitemapPlugin()],
    frontend_packages=["motion"],
)
