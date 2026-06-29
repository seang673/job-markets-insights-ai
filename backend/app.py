import gradio as gr
import requests
import plotly.express as px

API = "http://localhost:8000"

# Special dropdown option that aggregates insights across every saved role.
# Sending no `role` param makes the backend skip its WHERE filter.
ALL_ROLES = "All Roles"

# Same idea for seniority: the sentinel option omits the `seniority` param so
# the backend aggregates across every level. The remaining values mirror the
# fixed set the LLM extractor emits (see app/llm/extractor.py).
ALL_SENIORITIES = "All Seniorities"
SENIORITY_LEVELS = [
    ALL_SENIORITIES,
    "Junior",
    "Mid-Level",
    "Senior",
    "Lead",
    "Principal",
    "Unknown",
]

# ---- UI styling -------------------------------------------------------------

# A richer theme than the default: indigo accents, slate neutrals, and a
# slightly larger, bolder type scale so headings and labels stand out.
THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.amber,
    secondary_hue=gr.themes.colors.pink,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="*neutral_50",
    block_background_fill="white",
    block_shadow="0 1px 3px rgba(0,0,0,0.08)",
    block_radius="14px",
)

CSS = """
/* Soft gradient backdrop instead of flat white */
.gradio-container {
    background: linear-gradient(160deg, #fefce8 0%, #f0f9ff 50%, #fdf2f8 100%) !important;
}

/* App heading */
#app-title h1 {
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #f59e0b, #ec4899);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.1rem;
}
#app-subtitle p {
    color: #64748b;
    font-size: 1.02rem;
    margin-top: 0;
}

/* Make the action buttons compact and natural-sized rather than full width */
#action-row { align-items: flex-end; gap: 10px; }
#scrape-btn, #delete-btn {
    max-width: 220px;
    font-weight: 600;
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}

/* Stronger summary text */
#summary-box { font-size: 1.05rem; }
"""

# Give the Plotly charts a transparent backdrop so they blend with the cards.
def _style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#334155"),
        title_font=dict(size=18, color="#1e293b"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig

#Loading and displaying insights for job
def load_insights(role, seniority=ALL_SENIORITIES):
    # Each sentinel ("All Roles"/"All Seniorities") => omit that param so the
    # backend skips the corresponding WHERE filter and aggregates over it.
    params = {}
    if role and role != ALL_ROLES:
        params["role"] = role
    if seniority and seniority != ALL_SENIORITIES:
        params["seniority"] = seniority

    res = requests.get(f"{API}/api/insights/overview", params=params).json()
    if (
        "top_skills" not in res
        or not res["top_skills"]
        or res.get("total_jobs", 0) == 0
    ):
        role_scope = "any role" if role == ALL_ROLES else f"'{role}'"
        sen_scope = "" if seniority == ALL_SENIORITIES else f" at '{seniority}' level"
        msg = f"**No job data found for {role_scope}{sen_scope}.**\nTry scraping some jobs first."
        empty_fig = px.scatter()  # blank placeholder chart
        return msg, empty_fig, empty_fig, empty_fig, empty_fig

    # Build charts
    skills_fig = _style_fig(px.bar(
        res["top_skills"],
        x="count",
        y="name",
        orientation="h",
        title="Top Skills",
        color_discrete_sequence=["#22c55e"]
    ))

    tech_fig = _style_fig(px.bar(
        res["top_tech_stack"],
        x="count",
        y="name",
        orientation="h",
        title="Top Tech Stack",
        color_discrete_sequence=["#f59e0b"]
    ))

    seniority_fig = _style_fig(px.pie(
        res["seniority_distribution"],
        names="level",
        values="count",
        title="Seniority Distribution",
        color_discrete_sequence=["#ef4444", "#f59e0b", "#22c55e", "#0ea5e9", "#8b5cf6", "#ec4899"]
    ))

    # Salary box-plot. Grouped adaptively by the backend (per-role in the
    # "All Roles" view, per-seniority otherwise). JSearch reports salary on
    # only a minority of postings, so this can be empty even when other charts
    # are populated — fall back to a blank placeholder in that case.
    salary_data = res.get("salary_data", [])
    salary_count = len(salary_data)
    if salary_data:
        group_label = res.get("salary_group_by", "group").capitalize()
        salary_fig = _style_fig(px.box(
            salary_data,
            x="group",
            y="salary",
            points="outliers",
            title=f"Salary Distribution by {group_label} (annualized USD)",
            color="group",
            color_discrete_sequence=px.colors.qualitative.Set2,
        ))
        salary_fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Annual salary (USD)")
    else:
        salary_fig = px.scatter()  # blank placeholder when no salary reported

    label = ALL_ROLES if role == ALL_ROLES else res["role"]
    sen_label = ALL_SENIORITIES if seniority == ALL_SENIORITIES else seniority
    summary = (
        f"**Total Number of {label} Jobs:** {res['total_jobs']}  \n"
        f"**Role:** {label}  \n"
        f"**Seniority:** {sen_label}  \n"
        f"**Postings with salary data:** {salary_count}"
        + ("  _(salary is sparsely reported — scrape more to populate the box-plot)_" if salary_count == 0 else "")
    )

    return summary, skills_fig, tech_fig, seniority_fig, salary_fig

# Load insights and toggle the action buttons. Scraping targets a single role,
# so it's disabled in the "All Roles" view; delete stays enabled there and
# clears every posting in the database.
def load_view(role, seniority):
    summary, skills_fig, tech_fig, seniority_fig, salary_fig = load_insights(role, seniority)
    scrape_enabled = role != ALL_ROLES
    return (
        summary,
        skills_fig,
        tech_fig,
        seniority_fig,
        salary_fig,
        gr.update(interactive=scrape_enabled),
        gr.update(interactive=True),
    )

#Scraping jobs and refreshing insights
def scrape_and_refresh(role, seniority):
    # Scraping is role-specific (it drives the JSearch query); the seniority
    # selection is only a view filter, applied when we refresh insights below.
    if role == ALL_ROLES:
        gr.Warning("Select a specific role to scrape jobs.")
        return
    yield (
          # button
        None, None, None, None, None,  # placeholders for charts/summary
        gr.update(value="Scraping...", interactive=False),
        gr.update(value="Delete Scraped Jobs", variant="stop", interactive=False)
    )
    gr.Info(f"Scraping more jobs for {role} role, this usually takes around 1 minute...")

    # Trigger scraping
    requests.post(f"{API}/api/scrape?role={role}")

    gr.Info("Scraping complete!")

    # After scraping, fetch updated insights
    summary, skills_fig, tech_fig, seniority_fig, salary_fig = load_insights(role, seniority)

    yield(
        summary,
        skills_fig,
        tech_fig,
        seniority_fig,
        salary_fig,
        gr.update(value="Scrape More Jobs", interactive=True),
        gr.update(value="Delete Scraped Jobs", variant="stop", interactive=True)
    )

    return (summary, skills_fig, tech_fig, seniority_fig, salary_fig, gr.update(value="Scrape More Jobs", interactive=True))

#Delete jobs, narrowed by the active role and seniority filters. With both set
#to their "All ..." sentinels this deletes every posting in the database.
def delete_jobs(role, seniority):
    is_all_roles = role == ALL_ROLES
    is_all_seniorities = seniority == ALL_SENIORITIES
    try:
        yield (
          # button
            None, None, None, None, None,  # placeholders for charts/summary
            gr.update(value="Scrape More Jobs", interactive=False),
            gr.update(value="Deleting...", variant="stop", interactive=False)
        )
        # Omit each param at its sentinel so the backend skips that filter:
        # no role => every role, no seniority => every level.
        params = {}
        if not is_all_roles:
            params["role"] = role
        if not is_all_seniorities:
            params["seniority"] = seniority
        resp = requests.delete(f"{API}/api/jobs", params=params).json()
        deleted = resp.get("deleted", 0)

        role_scope = "all roles" if is_all_roles else f"role: {role}"
        sen_scope = "" if is_all_seniorities else f", seniority: {seniority}"
        gr.Info(f"Deleted {deleted} jobs for {role_scope}{sen_scope}")
        summary, skills_fig, tech_fig, seniority_fig, salary_fig = load_insights(role, seniority)

        yield(
            summary,
            skills_fig,
            tech_fig,
            seniority_fig,
            salary_fig,
            # Scrape stays disabled while viewing "All Roles".
            gr.update(value="Scrape More Jobs", interactive=not is_all_roles),
            gr.update(value="Delete Scraped Jobs", variant="stop", interactive=True)
        )

    except Exception as e:
        gr.Error(f"Failed to delete jobs: {e}")
        return None, None, None, None, None, gr.update(value="Scrape More Jobs", interactive=True),  gr.update(value="Delete Scraped Jobs", variant="stop", interactive=True)


with gr.Blocks(theme=THEME, css=CSS, title="Job Market Insights") as demo:
    gr.Markdown("# Job Market Insights In Technology", elem_id="app-title")
    gr.Markdown(
        "Explore in-demand skills, tech stacks, and seniority trends across tech roles.",
        elem_id="app-subtitle",
    )

    with gr.Row(elem_id="action-row"):
        role = gr.Dropdown(
            [ALL_ROLES,
             "Software Engineer",
             "Data Scientist",
             "Machine Learning Engineer",
             "Quality Assurance Engineer",
             "Backend Engineer",
             "Frontend Engineer",
             "DevOps Engineer",
             "Full Stack Engineer",
             "AI Engineer"
            ],
            label="Select Role",
            value=ALL_ROLES,
            scale=3,
        )
        seniority = gr.Dropdown(
            SENIORITY_LEVELS,
            label="Select Seniority",
            value=ALL_SENIORITIES,
            scale=2,
        )
        scrape_btn = gr.Button(
            "Scrape More Jobs", variant="primary", size="sm",
            scale=1, min_width=160, elem_id="scrape-btn",
        )
        delete_btn = gr.Button(
            "Delete Scraped Jobs", variant="stop", size="sm",
            scale=1, min_width=160, elem_id="delete-btn",
        )

    summary = gr.Markdown(elem_id="summary-box")

    with gr.Row():
        skills_chart = gr.Plot()
        tech_chart = gr.Plot()

    seniority_chart = gr.Plot()

    # Salary box-plot — full width below the pie since box-plots read better wide.
    salary_chart = gr.Plot()

    #Load insights on initial page load
    demo.load(
        load_view,
        inputs=[role, seniority],
        outputs=[summary, skills_chart, tech_chart, seniority_chart, salary_chart, scrape_btn, delete_btn]
    )

    #Auto-load insights on role change
    role.change(
        load_view,
        inputs=[role, seniority],
        outputs=[summary, skills_chart, tech_chart, seniority_chart, salary_chart, scrape_btn, delete_btn]
    )

    #Auto-load insights on seniority change
    seniority.change(
        load_view,
        inputs=[role, seniority],
        outputs=[summary, skills_chart, tech_chart, seniority_chart, salary_chart, scrape_btn, delete_btn]
    )

    scrape_btn.click(
        scrape_and_refresh,
        inputs=[role, seniority],
        outputs=[summary, skills_chart, tech_chart, seniority_chart, salary_chart, scrape_btn, delete_btn]
    )

    delete_btn.click(
        delete_jobs,
        inputs=[role, seniority],
        outputs=[summary, skills_chart, tech_chart, seniority_chart, salary_chart, scrape_btn, delete_btn]
    )

demo.launch()