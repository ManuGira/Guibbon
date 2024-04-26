import os
import sys

PAYLOAD = """
        <div style="padding:5px">
            <div class="topnav">
              <span>version</span>
              <select id="version_select" onchange="onVersionChange();">
                <<<OPTION_GROUP_HTML>>>
              </select>
            </div>
            <script>
            function onVersionChange() {
              let current_version = "<<<CURRENT_VERSION>>>"
              let target_version = document.getElementById("version_select").value;
              let current_url = window.location.pathname;
              let target_url = current_url.replace(current_version, target_version);
              window.location.pathname = target_url;
            }
            </script>
        </div>

"""

INDEX_REDIRECT = """<!DOCTYPE HTML>
<html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url=<<<LATEST_STABLE_RELEASE>>>">
        <script type="text/javascript">
            window.location.href = "<<<LATEST_STABLE_RELEASE>>>"
        </script>
        <title>Guibbon Page Redirection</title>
    </head>
    <body>
        If you are not redirected automatically, follow this <a href='<<<LATEST_STABLE_RELEASE>>>'>link to documentation of latest stable release (<<<LATEST_STABLE_RELEASE>>>)</a>.
    </body>
</html>
"""


def create_option_tag(target_version, is_default=False):
    selected = ' selected="selected"' if is_default else ''
    return f'<option value="{target_version}"{selected}>{target_version}</option>'


def create_option_group(versions_list, default_version):
    OPTION_GROUP_HTML = []
    indent = "\n" + 4 * "  "
    for version in versions_list:
        option_html = create_option_tag(
            version,
            is_default=version == default_version,
        )
        OPTION_GROUP_HTML.append(option_html)
    OPTION_GROUP_HTML = indent.join(OPTION_GROUP_HTML)
    return OPTION_GROUP_HTML


def insert_payload_in_html_file(filepath, payload):
    print(filepath)
    # load file
    with open(filepath) as foo:
        html_lines = foo.readlines()

    html_out = ""
    head_closed = False  # True after passing the first occurence of "</head>"
    inserted = False
    for line in html_lines:
        html_out += line

        if "</head>" in line:
            head_closed = True

        # find the first occurence of "<body" after first occurence of "</head>"
        if not inserted and head_closed and line.strip().startswith("<body"):
            # insert payload
            html_out += payload
            inserted = True

    # save file
    with open(filepath, "w") as foo:
        foo.write(html_out)


def hash_vesion(version):
    is_dev = version.endswith("-dev")
    version = version[1:].replace("-dev", "")
    MAJ, MIN, BUILD = [int(v) for v in version.split(".")]
    assert max(MAJ, MIN, BUILD) < 10000
    REL = "0" if is_dev else "1"
    return f"{MAJ}{MIN:04}{BUILD:04}{REL}"


def generate_index_page(site_dir, latest_stable_release):
    index_html_file = os.path.join(site_dir, "index.html")
    index_html = INDEX_REDIRECT.replace("<<<LATEST_STABLE_RELEASE>>>", latest_stable_release)
    with open(index_html_file, "w") as fp:
        fp.write(index_html)


def main():
    site_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "site")
    versions = [dirname for dirname in os.listdir(site_dir) if os.path.isdir(os.path.join(site_dir, dirname))]
    print(versions)
    versions = sorted(versions, key=hash_vesion, reverse=True)

    # create root index.html that redirect to latest stable release
    latest_stable_release = [v for v in versions if not v.endswith("-dev")][0]
    generate_index_page(site_dir, latest_stable_release)

    # for each version, list the html files
    for version in versions:
        version_dir = os.path.join(site_dir, version)
        filepaths = []
        for res in os.walk(version_dir):
            for filename in res[2]:
                filepath = os.path.join(res[0], filename)
                filepaths.append(filepath)
        filepaths = [s for s in filepaths if s.endswith(".html")]
        filepaths = [s for s in filepaths if not s.endswith("404.html")]
        print(filepaths)

        for filepath in filepaths:
            OPTION_GROUP_HTML = create_option_group(versions, default_version=version)
            payload = PAYLOAD.replace("<<<OPTION_GROUP_HTML>>>", OPTION_GROUP_HTML).replace("<<<CURRENT_VERSION>>>", version)
            insert_payload_in_html_file(filepath, payload)


if __name__ == '__main__':
    main()
