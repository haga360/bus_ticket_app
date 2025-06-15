
from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

DB = 'tickets.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())

@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return render_template_string(f.read())

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.json
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tickets (name, origin, destination, date, time, seat, fare) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (data['name'], data['origin'], data['destination'], data['date'], data['time'], data['seat'], data['fare']))
        conn.commit()
    return jsonify({'status': 'success'})

@app.route('/ticket-pdf')
def ticket_pdf():
    name = request.args.get('name', 'Unknown')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
    ticket = c.fetchone()
    conn.close()

    if not ticket:
        return "Ticket not found", 404

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"Bus Ticket for {ticket[1]}")
    p.drawString(100, 730, f"From: {ticket[2]}")
    p.drawString(100, 710, f"To: {ticket[3]}")
    p.drawString(100, 690, f"Date: {ticket[4]}")
    p.drawString(100, 670, f"Time: {ticket[5]}")
    p.drawString(100, 650, f"Seat: {ticket[6]}")
    p.drawString(100, 630, f"Fare: TZS {ticket[7]}")
    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="ticket.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
