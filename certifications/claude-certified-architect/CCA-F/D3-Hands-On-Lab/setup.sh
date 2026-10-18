#!/usr/bin/env bash
# CCA-F Domain 3 hands-on lab — creates a throwaway repo to experiment in.
# Safe: everything lives under ~/cca-f-lab. Delete with:  rm -rf ~/cca-f-lab
set -euo pipefail

LAB="${1:-$HOME/cca-f-lab}"
if [ -e "$LAB" ]; then
  echo "!! $LAB already exists. Remove it first:  rm -rf $LAB"
  exit 1
fi

mkdir -p "$LAB"/{services/orders,services/billing,web/src/components,infra}
cd "$LAB"
git init -q

# --- a small tree with the properties D3 questions care about -----------------
# Test files sit BESIDE their sources in both trees. This is the detail that makes
# directory-scoped CLAUDE.md insufficient and path-glob rules necessary.
cat > services/orders/order.go <<'EOF'
package orders

type Order struct {
	ID     string
	Total  int64 // minor units
	Status string
}

func (o *Order) IsSettled() bool { return o.Status == "settled" }
EOF

cat > services/orders/order_test.go <<'EOF'
package orders

import "testing"

func TestIsSettled(t *testing.T) {
	o := &Order{Status: "settled"}
	if !o.IsSettled() {
		t.Fatal("expected settled")
	}
}
EOF

cat > services/billing/invoice.go <<'EOF'
package billing

type Invoice struct {
	Number string
	Amount int64
}
EOF

cat > web/src/components/Button.tsx <<'EOF'
export function Button({ label }: { label: string }) {
  return <button>{label}</button>;
}
EOF

cat > web/src/components/Button.test.tsx <<'EOF'
import { Button } from "./Button";

test("renders label", () => {
  expect(Button({ label: "Save" })).toBeTruthy();
});
EOF

cat > infra/main.tf <<'EOF'
resource "aws_s3_bucket" "artifacts" {
  bucket = "cca-f-lab-artifacts"
}
EOF

cat > README.md <<'EOF'
# CCA-F Domain 3 lab

A throwaway repo for practising Claude Code configuration.
Nothing here is real. Delete the whole directory when you are done.
EOF

git add -A
git commit -q -m "lab baseline"

echo "Lab created at: $LAB"
echo
echo "Tree:"
find . -type f -not -path "./.git/*" | sort | sed 's|^\./|  |'
echo
echo "Next: open $LAB in your editor and start Exercise 1 in the lab guide."
