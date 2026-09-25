#!/bin/sh
# Clone the charter at the locked commit and refuse unless the author signed it. Run from the repo root.
set -eu
. cage/charter.lock
rm -rf charter
git clone -q https://github.com/gfrmin/wald-charter charter
cd charter
git -c gpg.format=ssh -c gpg.ssh.allowedSignersFile=../cage/allowed_signers tag -v "$TAG" > ../.tagcheck 2>&1 || true
grep -q 'Good "git" signature for author@wald' ../.tagcheck || { echo "tag $TAG is not signed by author@wald"; cat ../.tagcheck; exit 1; }
[ "$(git rev-list -n1 "$TAG")" = "$SHA" ] || { echo "tag $TAG does not point at the locked commit"; exit 1; }
git checkout -q "$SHA"
git diff --quiet charter-v0 -- CHARTER.md || { echo "CHARTER.md differs from the signed page charter-v0"; exit 1; }
git diff --quiet surface-v0 -- SURFACE.md || { echo "SURFACE.md differs from the signed page surface-v0"; exit 1; }
git diff --quiet charter-v0.1 -- CHARTER-v0.1.md || { echo "CHARTER-v0.1.md differs from the signed page charter-v0.1"; exit 1; }
git diff --quiet surface-v0.1 -- SURFACE-v0.1.md || { echo "SURFACE-v0.1.md differs from the signed page surface-v0.1"; exit 1; }
git diff --quiet charter-v0.2 -- CHARTER-v0.2.md || { echo "CHARTER-v0.2.md differs from the signed page charter-v0.2"; exit 1; }
git diff --quiet surface-v0.2 -- SURFACE-v0.2.md || { echo "SURFACE-v0.2.md differs from the signed page surface-v0.2"; exit 1; }
echo "charter ok: $TAG at $SHA, signed by author@wald, pages unchanged since charter-v0, surface-v0, charter-v0.1, surface-v0.1, charter-v0.2, surface-v0.2"
