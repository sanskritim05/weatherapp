
import sqlite3, json, requests, csv
from io import StringIO, BytesIO
from fpdf import FPDF
from flask import Flask, request, render_template, send_file


def export(filetype, app):

    conn = sqlite3.connect("weather.db")
    c = conn.cursor()
    c.execute("SELECT city, date, temperature, description FROM weather ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    if filetype == "json":
        data = [{"city": city, "date": date, "temperature": temp, "description": desc}
                for city, date, temp, desc in rows]
        return app.response_class(
            response=json.dumps(data, indent=4),
            mimetype='application/json',
            headers={"Content-Disposition": "attachment;filename=weather.json"}
        )

    elif filetype == "csv":
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["City", "Date", "Temperature", "Description"])
        cw.writerows(rows)
        output = si.getvalue().encode("utf-8")
        return send_file(BytesIO(output),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name="weather.csv")

    elif filetype == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Saved Weather Forecasts", ln=True, align='C')
        pdf.ln(10)

        for city, date, temp, desc in rows:
            pdf.cell(200, 10, txt=f"{date} - {city}: {temp}°F, {desc}", ln=True)

        #pdf_output = BytesIO()
        #pdf.output(pdf_output)
        #pdf_output.seek(0)
        pdf.output("weather.pdf")
        return send_file("weather.pdf",
                         mimetype='application/pdf',
                         as_attachment=True,
                         download_name="weather.pdf")
    
    else:
        return "Invalid export format", 400