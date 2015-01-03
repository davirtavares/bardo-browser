#!/usr/bin/env sh

python -c "import pageloader; pageloader.load_page.delay('$1')"
