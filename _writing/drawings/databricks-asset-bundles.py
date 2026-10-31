"""Drawings for 'CI/CD for Databricks with Asset Bundles'. Globals kit, figure, E, ROOT are injected."""


def _hotel(x, y, w, h, name):
    """A small hotel building with windows and a door; top-left at (x, y)."""
    d = f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>'
    d += f'<path class="hz" d="M{x - 8},{y} L{x + w / 2},{y - 28} L{x + w + 8},{y} Z"/>'
    for r in range(2):
        for c in range(3):
            wx = x + 18 + c * ((w - 36 - 22) / 2)
            wy = y + 16 + r * 30
            d += f'<rect class="pf pf-bx" x="{wx:.0f}" y="{wy}" width="22" height="18" rx="2"/>'
    d += f'<rect class="hz" x="{x + w / 2 - 14:.0f}" y="{y + h - 34}" width="28" height="34" rx="3"/>'
    d += kit.text(x + w / 2, y + h + 26, name, "bd", "middle")
    return d


def drawing_dab_suitcase():
    t, p = kit.text, kit.path
    d = t(500, 24, "pack it once, in Git; carry the same bag everywhere", "sm", "middle")
    # the suitcase
    d += '<rect class="hz" x="70" y="130" width="190" height="130" rx="12"/>'
    d += '<rect class="pf pf-solid" x="78" y="138" width="174" height="114" rx="9"/>'
    d += '<path class="hz" d="M135,130 L135,108 Q135,100 143,100 L187,100 Q195,100 195,108 L195,130" style="fill:none"/>'
    d += '<line class="ln" x1="120" y1="138" x2="120" y2="252"/><line class="ln" x1="210" y1="138" x2="210" y2="252"/>'
    d += t(165, 186, "the bundle", "bd", "middle")
    d += t(165, 210, ["jobs, pipelines,", "code, settings"], "sm", "middle")
    d += t(165, 296, "one databricks.yml", "sm", "middle")
    # three hotels
    hotels = [(430, "dev"), (610, "test"), (790, "prod")]
    for hx, name in hotels:
        d += _hotel(hx, 150, 150, 120, name)
    d += t(505, 320, ["your own copy,", "schedules paused"], "sm", "middle")
    d += t(685, 320, ["a shared workspace,", "small test data"], "sm", "middle")
    d += t(865, 320, ["runs as a service", "principal, for real"], "sm", "middle")
    # routes
    d += p("M262,165 Q380,70 498,116", "ln")
    d += p("M262,152 Q470,20 678,116", "ln")
    d += p("M262,140 Q560,-10 858,116", "ln")
    return figure(1000, 360, d, "A suitcase labelled the bundle, holding jobs, pipelines, code and settings, with three curved arrows to three hotels labelled dev, test and prod. Under each hotel: your own copy with schedules paused; a shared workspace with small test data; runs as a service principal, for real.",
                  "One bundle, three targets. The contents stay the same; only the hotel changes.")


def drawing_dab_folder():
    b, t = kit.box, kit.text
    d = t(500, 24, "everything a job needs lives in one Git repository", "sm", "middle")
    # a folder icon
    d += '<path class="hz" d="M40,70 L100,70 L112,84 L190,84 L190,150 L40,150 Z"/>'
    d += t(115, 175, "sales_pipelines/", "bd", "middle")
    # tree lines
    d += '<line class="ln" x1="230" y1="75" x2="230" y2="342"/>'
    rows = [
        (75, "databricks.yml", ["the bundle's name, variables", "and targets"], "solid"),
        (165, "resources/", ["one YAML file per job", "or pipeline"], "bx"),
        (255, "src/", ["notebooks and Python", "the jobs run"], "bx"),
        (345, "tests/", ["unit tests for the", "transformation code"], "bxs"),
    ]
    for y, name, sub, kind in rows:
        d += f'<line class="ln" x1="230" y1="{y}" x2="260" y2="{y}"/>'
        d += b(262, y - 35, 300, 70, name, "", kind)
        d += t(590, y - 6, sub, "sm", "start")
    return figure(1000, 395, d, "A folder named sales_pipelines with four entries: databricks.yml holds the bundle's name, variables and targets; resources holds one YAML file per job or pipeline; src holds the notebooks and Python the jobs run; tests holds unit tests for the transformation code.",
                  "The layout most bundles end up with. The names are a habit, not a rule.")


def drawing_dab_pipeline():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "every step is a machine, except one: a person approves prod", "sm", "middle")
    # row 1: on the pull request
    d += t(20, 60, "ON EVERY PULL REQUEST", "lbl", "start")
    d += kit.num(105, 80, 1) + b(20, 95, 170, 75, "Pull request", "someone opens one", "bxm")
    d += a(192, 132, 228, 132)
    d += kit.num(315, 80, 2) + b(230, 95, 170, 75, "Validate", "bundle validate", "bxs")
    d += a(402, 132, 438, 132)
    d += kit.num(525, 80, 3) + b(440, 95, 170, 75, "Unit tests", "pytest, no cluster", "bxs")
    d += a(612, 132, 648, 132)
    d += kit.num(735, 80, 4) + b(650, 95, 170, 75, "Merge", "a reviewer agrees", "bx")
    # row 2: after merge
    d += t(20, 368, "AFTER MERGE, AS A SERVICE PRINCIPAL", "lbl", "start")
    d += kit.path("M735,172 C735,225 105,195 105,236", "ln")
    d += kit.num(105, 250, 5) + b(20, 265, 170, 75, "Deploy to test", "bundle deploy", "bx")
    d += a(192, 302, 228, 302)
    d += kit.num(315, 250, 6) + b(230, 265, 170, 75, "Integration run", "bundle run, small data", "bxs")
    d += a(402, 302, 438, 302)
    d += kit.num(525, 250, 7) + b(440, 265, 170, 75, "Approve", "a person says yes", "bxm")
    d += a(612, 302, 648, 302)
    d += kit.num(735, 250, 8) + b(650, 265, 170, 75, "Deploy to prod", "same bundle", "solid")
    # stick person by approve
    d += ('<circle class="bx" cx="900" cy="262" r="13"/><line class="lnc" x1="900" y1="275" x2="900" y2="315"/>'
          '<line class="lnc" x1="900" y1="315" x2="888" y2="340"/><line class="lnc" x1="900" y1="315" x2="912" y2="340"/>'
          '<line class="lnc" x1="900" y1="288" x2="880" y2="300"/><line class="lnc" x1="900" y1="288" x2="922" y2="270"/>')
    d += t(900, 368, "the only human step", "sm", "middle")
    return figure(1000, 385, d, "Eight numbered steps in two rows. On every pull request: pull request, validate, unit tests, merge. After merge, running as a service principal: deploy to test, integration run on small data, a person approves, deploy to prod with the same bundle. A stick person stands by the approve step.",
                  "A simple pipeline. A mistake caught at step 2 or 3 costs a minute; caught in prod, it costs a morning.")


def drawing_dab_dev_mode():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "same bundle, deployed three times; nobody steps on anyone", "sm", "middle")
    d += b(30, 150, 200, 90, "The bundle", ["job: daily_orders"], "solid")
    d += a(232, 175, 368, 85)
    d += a(232, 195, 368, 195)
    d += a(232, 215, 368, 305)
    d += b(370, 50, 330, 70, "[dev priya] daily_orders", "Priya runs deploy", "bx")
    d += b(370, 160, 330, 70, "[dev arjun] daily_orders", "Arjun runs deploy", "bx")
    d += b(370, 270, 330, 70, "daily_orders", "CI runs deploy -t prod", "bxs")
    d += t(725, 80, ["in Priya's own folder,", "schedule paused"], "sm", "start")
    d += t(725, 190, ["in Arjun's own folder,", "schedule paused"], "sm", "start")
    d += t(725, 300, ["mode: production,", "schedule on, no prefix"], "sm", "start")
    return figure(1000, 360, d, "One bundle containing the job daily_orders, deployed three times. Priya's deploy creates [dev priya] daily_orders in her own folder with the schedule paused. Arjun's creates [dev arjun] daily_orders. CI's deploy to prod creates daily_orders with the schedule on and no prefix.",
                  "Development mode gives every person their own named copy. Production mode gives one real one.")


DRAWINGS = {
    "dab-suitcase": drawing_dab_suitcase,
    "dab-folder": drawing_dab_folder,
    "dab-pipeline": drawing_dab_pipeline,
    "dab-dev-mode": drawing_dab_dev_mode,
}
