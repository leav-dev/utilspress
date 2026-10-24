import flet as ft


def _format_freed(bytes_val):
    if bytes_val >= 1024 ** 3:
        return f"{bytes_val / (1024 ** 3):.2f} GB"
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    if bytes_val >= 1024:
        return f"{bytes_val / 1024:.2f} KB"
    return f"{int(bytes_val)} B"


def build_results_table(results, operation, output_dir):
    if not results:
        return ft.Column()

    total_orig = sum(r["original_size"] for r in results)
    total_final = sum(r["final_size"] for r in results)
    avg = round((1 - total_final / total_orig) * 100, 1) if total_orig else 0
    freed = max(0, total_orig - total_final)
    freed_str = _format_freed(freed)
    output_lower = str(output_dir).lower()
    in_place = ("reemplazad" in output_lower or "in-place" in output_lower or "inplace" in output_lower)

    cols = [ft.DataColumn(ft.Text("Archivo", size=12))]
    if operation == "convert":
        cols.append(ft.DataColumn(ft.Text("Archivo nuevo", size=12)))
    if operation == "resize":
        cols.append(ft.DataColumn(ft.Text("Original", size=12)))
        cols.append(ft.DataColumn(ft.Text("Final", size=12)))
    cols.append(ft.DataColumn(ft.Text("Tamaño original", size=12)))
    cols.append(ft.DataColumn(ft.Text("Tamaño final", size=12)))
    if operation in ("compress", "pdf"):
        cols.append(ft.DataColumn(ft.Text("Ahorro", size=12)))
    if operation == "pdf":
        cols.append(ft.DataColumn(ft.Text("Preset", size=12)))

    rows = []
    for r in results:
        cells = [ft.DataCell(ft.Text(r["file"], size=12))]
        if operation == "convert":
            cells.append(ft.DataCell(ft.Text(r["new_file"], size=12)))
        if operation == "resize":
            cells.append(ft.DataCell(ft.Text(r["original_dims"], size=12)))
            cells.append(ft.DataCell(ft.Text(r["final_dims"], size=12)))
        cells.append(ft.DataCell(ft.Text(r["original_size_str"], size=12)))
        cells.append(ft.DataCell(ft.Text(r["final_size_str"], size=12)))
        if operation in ("compress", "pdf"):
            cells.append(ft.DataCell(
                ft.Text(f"-{r['savings_percent']}%", size=12, color=ft.Colors.GREEN)
            ))
        if operation == "pdf":
            cells.append(ft.DataCell(ft.Text(r.get("preset", ""), size=12)))
        rows.append(ft.DataRow(cells=cells))

    noun = "PDF(s)" if operation == "pdf" else "archivo(s)"
    if in_place:
        footer = f"♻️ Reemplazados en: {output_dir} — espacio liberado {freed_str}"
    else:
        footer = f"📁 Guardado en: {output_dir}"
    return ft.Column([
        ft.Text(
            f"✅ Se procesaron {len(results)} {noun}  —  "
            f"Ahorro promedio: {avg}%",
            size=14,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text(
            f"💾 Total liberado: {freed_str}",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN,
        ),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        ft.DataTable(
            columns=cols,
            rows=rows,
            column_spacing=30,
        ),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        ft.Text(
            footer,
            size=11,
            color=ft.Colors.GREY_600,
        ),
    ])
