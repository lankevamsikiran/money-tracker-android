#!/usr/bin/env python3
"""Polish transaction history buttons and replace Android launcher icon.
Run at repository root: python3 polish_money_tracker.py
"""
from pathlib import Path
import base64,re,shutil
root=Path.cwd()
p=root/'app/src/main/assets/index.html'
if not p.exists(): raise SystemExit('ERROR: Run from money-tracker-android repository root.')
s=p.read_text(encoding='utf-8')
if 'historyFor(items)' not in s: raise SystemExit('ERROR: Grouped-transaction upgrade not found; no changes made.')
if 'history-action-row' in s: raise SystemExit('Already polished. No changes made.')
# Transaction row is flex; previous .actions buttons had flex:0, shrinking the text.
css="""
/* Comfortable, consistent transaction action buttons */
.history-item{align-items:flex-start;gap:14px;padding:17px 0}
.history-item>div:first-child{flex:1;min-width:0}
.history-item>b{flex-shrink:0;font-size:16px}
.history-action-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.history-action-row button{display:inline-flex;align-items:center;justify-content:center;gap:7px;flex:0 0 auto!important;min-width:104px!important;min-height:42px;padding:10px 14px!important;border:0;border-radius:11px;font-size:14px;font-weight:700;line-height:1.2;white-space:nowrap;cursor:pointer}
.history-action-row .edit-action{background:#e3f7ee;color:#087f5b}
.history-action-row .delete-action{background:#fff0f0;color:#bc2836}
.history-action-row svg{height:17px;width:17px;flex-shrink:0;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
"""
if '</style>' not in s: raise SystemExit('ERROR: Stylesheet end not found.')
s=s.replace('</style>',css+'</style>',1)
old="""<div class="actions"><button onclick="openEdit('${h.id}')">Edit</button><button class="danger" onclick="deletePersonTransaction('${h.id}')">Delete</button></div>"""
new="""<div class="history-action-row"><button class="edit-action" onclick="openEdit('${h.id}')" aria-label="Edit transaction"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L9 17l-4 1 1-4Z"/></svg>Edit</button><button class="delete-action" onclick="deletePersonTransaction('${h.id}')" aria-label="Delete transaction"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14M10 10v7M14 10v7"/></svg>Delete</button></div>"""
if old not in s: raise SystemExit('ERROR: Expected history action buttons not found; no changes made.')
s=s.replace(old,new,1)
backup=p.with_suffix('.html.before-icon-polish');shutil.copy2(p,backup);p.write_text(s,encoding='utf-8')
manifest=root/'app/src/main/AndroidManifest.xml'
if not manifest.exists(): raise SystemExit('ERROR: AndroidManifest.xml not found (HTML already updated).')
m=manifest.read_text(encoding='utf-8')
if 'android:icon=' not in m: raise SystemExit('ERROR: No launcher icon attribute found (HTML already updated).')
m2,n=re.subn(r'android:icon="[^"]+"','android:icon="@drawable/money_tracker_icon"',m,count=1)
if n!=1: raise SystemExit('ERROR: Could not replace launcher icon (HTML already updated).')
manifest.write_text(m2,encoding='utf-8')
icon=root/'app/src/main/res/drawable-nodpi/money_tracker_icon.png';icon.parent.mkdir(parents=True,exist_ok=True)
icon.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAFiElEQVR42u3dr25UTRzH4Z3JJrQKVS6gCoviEriINhgcCQaHIN0GgcOQ4DCkvQguAYVFcQGgUC2qKBJSWuj+OduZ+T6P5EVs95zf5/xmW/rOZgAAAECCMtoXtHN0cOGyMqXz49MiAIYduo9CMfCQG4Ri6CE3BsXgQ24IisGH3BAUgw+5ISgGH3JDUAw+5IagGn7IPQYXgw+520A1/JC7DVTDD7kRKAYfco8E1fBD7jZQDT/kRqAafsiNQDX8kBuBavghNwLV8ENuBKq3EXKtHQBPf+h3C6iGH3IjUA0/5EbAZwDgMwBPf0jcAqrhh9wIOAKAI4CnPyRuATYAsAF4+kPiFmADABuApz8kbgE2ALABePpD4hZgAwAbgKc/JG4BNgCwAQACYP2HqGOADQBsAIAAAALg/A8ZnwPYAMAGAAgAIABAaAB8AAjjujzfNgCwAQACAAgAIACAAAACAAgAIACAAAACAAgAIABAJ+ajf4GfX7xxlQfy4PVzb4IAGPpUf15bMXAEMPxigAC4IUSA6AC4EUSA0AC4AXAPhAbAhce9EBoAFxz3hCMAIABATACserg3bACAAAACACxl7i1gRGeLk6X+/u7iUABAMLJi4AgAV8Rg2Q1CAEAIBABGPh4IANgGBABsAwIAItAx3wbcsIfvX13555+evPTmIAApA8/4W8AIPy8gAAaf4AgIgMHHEQCDT+IW0O13Abb5f4Ux/H25f+eeN8EGYPCxBQy7ARh+CA/AVKue4XdPOAJ0sHb9vuBffn5ravj90E/e8Pd6DJiPcuE3EYF1ht/Qe/LbADqOwKrDb/ANvwAMtgkYfMOforohln/6G37DbwPo5Mb430awzPAbfEMvAKE3zI+nb90tOAKM5O67Z+4ABABPfwTA09/wIwCAAHj6e/ojAIAAxPH0RwAAAUg8/4MAWP9BAAABAAQAGIVfC86N7Tx+5E34h7K/JwAY+lQXX793FwNHAAz/xDEQAAy/CDgCtM73/w3/FBFo+TgwN+gY/twIVMOP4c89DvgMAMMfHAEBgGACAAKA9Z/EY4AAgA0AEABAAAABAAbn3wIQ7fzDx7/+LOm7IgKAwb/mvyWEwBEAw7/m3xMAGGz4UyIgABBMAPD0D94CBABsAIAAAAIACAAMZdUf7Bn5B4IEAGwAYAtIe/oLACIQPPyzmX8MRHgE/GtAEAKfAQACAAgAIACAAAACAAgAIACAANC/hN9+24qyvycAgAAAAoBjgPVfABABwy8AiIDhFwBEwPALACJg+AUAETD8k/AbgbhxBNJ/e84oQy8A2AgmsLs47O41OwJAMAEAAQAEABAAQAAAAWhTj99yYVy93o82ALABAAJg7YKo+9AGADYA9YXE+88GADYAFYbE+666GJB7vzkCgCOAKkPifVZdHMi9v+YjX6SzxYk7FoOf+hmAbQD3UeAGYBvA4AuAEGDwBeD6iysGpB8X5y465PKDQCAAgAAAAgAIACAAgAAAAgAIACAAgAAAAgAIANBrAM6PT4u3BcZ0eb5tAGADAAQAEAAgOAA+CITxXDXXNgCwAQACAAiAzwFg/PO/DQBsAIAAOAZA1PpvAwAbwOr1APp9+tsAwAawfkWA/p7+NgCwAWyuJkA/T38bANgANl8VoP2nvw0AbADT1QVo9+m/8gYgAtD/8DsCgCPA9moDtPP0X3sDEAHod/g3cgQQAehz+H0GAD4DuP0KAbczd7WlFwNsd95qiy8K2M6c1ZZfHDDtfNUeXiQwzVzVnl4sGP7N2sqQ7hwdXLiE0N6DtI7wRYDhbzgAIgBtzsutDKUjAbTxoKwJXyQY/oY2ANsAtPFAbOZJLAQY/OAACAEGXwCEAIMvAEKAwRcAMcDQC4AgYOAFQBQw7AAAAKv7BTwyC+KDjul7AAAAAElFTkSuQmCC'))
print('SUCCESS: Transaction Edit/Delete buttons improved and new wallet launcher icon installed.')
print('HTML backup:',backup)
print('Files to commit: app/src/main/assets/index.html, app/src/main/AndroidManifest.xml,',icon)
