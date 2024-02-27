from flask import Flask, render_template, url_for, request, redirect
import cx_Oracle
from datetime import datetime

app = Flask(__name__)

conn = cx_Oracle.connect("cardealer05", "pris05", "localhost/xe")

@app.route('/')
def base():
    return render_template('welcome.html')

@app.route('/clienti', methods=['POST', 'GET'])
def clienti():

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clienti")
    clienti = cursor.fetchall()

    cursor.execute("SELECT serie FROM masini WHERE vanduta LIKE 'NU'")
    serii_masini = cursor.fetchall()
    serii_masini = [serie[0] for serie in serii_masini]

    cursor.execute("SELECT tip FROM tip_garantii")
    tipuri_garantii = cursor.fetchall()
    tipuri_garantii = [tip[0] for tip in tipuri_garantii]

    cursor.execute("SELECT ID FROM clienti")
    IDs = cursor.fetchall()
    IDs = [ID[0] for ID in IDs]

    try:
        if request.method == 'POST':
            if 'nume' in request.form:
                nume = request.form['nume']
                prenume = request.form['prenume']
                email = request.form['email']
                telefon = request.form['telefon']
                adresa = request.form['adresa']
                tip_garantie = request.form['tip_garantie']
                serie_masina = request.form['serie_masina']

                cursor.execute("UPDATE masini SET vanduta = 'DA' WHERE serie = :serie_masina", serie_masina=serie_masina)

                cursor.execute(
                    "INSERT INTO clienti (Nume, Prenume, Email, Telefon, Adresa, Tip_garantie, Serie) "
                    "VALUES (:nume, :prenume, :email, :telefon, :adresa, :tip_garantie, :serie_masina)",
                    nume=nume, prenume=prenume, email=email, telefon=telefon, adresa=adresa,
                    tip_garantie=tip_garantie, serie_masina = serie_masina)

                cursor.execute("SELECT ID FROM clienti WHERE telefon = :telefon", telefon = telefon)
                ID = cursor.fetchone()[0]

                cursor.execute("SELECT pret FROM tip_garantii WHERE tip= :tip_garantie", tip_garantie = tip_garantie)
                pret_garantie = cursor.fetchone()[0]

                if tip_garantie == 'Normala':
                    cursor.execute("SELECT ADD_MONTHS(SYSDATE, 12 * 3) FROM DUAL")
                elif tip_garantie == '1 An':
                    cursor.execute("SELECT ADD_MONTHS(SYSDATE, 12 * (3 + 1)) FROM DUAL")
                elif tip_garantie == '2 Ani':
                    cursor.execute("SELECT ADD_MONTHS(SYSDATE, 12 * (3 + 2)) FROM DUAL")
                elif tip_garantie == '3 Ani':
                    cursor.execute("SELECT ADD_MONTHS(SYSDATE, 12 * (3 + 3)) FROM DUAL")
                data_expirare = cursor.fetchone()[0]
                data_expirare = data_expirare.strftime('%d-%b-%Y')

                cursor.execute("INSERT INTO garantii (ID, Nume, Tip_garantie, Data_expirare, Pret_garantie) VALUES (:ID, :nume, :tip_garantie, :data_expirare, :pret_garantie)",
                    ID=ID, nume=nume, tip_garantie=tip_garantie, data_expirare=data_expirare, pret_garantie=pret_garantie)

                cursor.execute("SELECT pret FROM masini WHERE serie=:serie", serie=serie_masina)
                cost_total = cursor.fetchone()[0]
                cost_total = cost_total + pret_garantie
                cursor.execute("SELECT TO_DATE(SYSDATE, 'DD-MM-YY') FROM DUAL")
                data_cumpararii = cursor.fetchone()[0]
                data_cumpararii=data_cumpararii.strftime('%d-%b-%Y')
                cursor.execute(
                    "INSERT INTO vanzari (ID, Nume, Prenume, Data_cumpararii, Cost_total) VALUES (:id, :nume, :prenume, :data_cumpararii, :cost_total)",
                    id=ID, nume=nume, prenume=prenume, data_cumpararii=data_cumpararii, cost_total=cost_total)

                conn.commit()

                return redirect(url_for('clienti'))

            elif 'ID' in request.form:
                ID = request.form['ID']
                cursor.execute("DELETE FROM vanzari WHERE ID=:ID", ID=ID)
                cursor.execute("DELETE FROM garantii WHERE ID=:ID", ID=ID)
                cursor.execute("SELECT serie FROM clienti WHERE ID=:ID", ID=ID)
                serie = cursor.fetchone()[0]
                cursor.execute("DELETE FROM clienti WHERE ID=:ID", ID=ID)
                cursor.execute("DELETE FROM masini WHERE serie=:serie", serie=serie)

                conn.commit()

            return redirect(url_for('clienti'))

    except Exception as e:
        conn.rollback()
        return f"Eroare: {str(e)}"
    finally:
        cursor.close()

    return render_template('clienti.html', clienti=clienti, serii_masini=serii_masini, tipuri_garantii=tipuri_garantii, IDs=IDs)


@app.route('/masini', methods=['POST', 'GET'])
def masini():
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM masini")
        masini = cursor.fetchall()

        for i in range(len(masini)):
            masina = masini[i]
            masina = [round(value, 1) if isinstance(value, float) else value for value in masina]
            masini[i] = masina

        if request.method == 'POST':
            marca = request.form['marca']
            model = request.form['model']
            an_fabricatie = request.form['an_fabricatie']
            culoare = request.form['culoare']
            motor = request.form['motor']
            tip_combustibil = request.form['tip_combustibil']
            pret = request.form['pret']
            print(marca, model, an_fabricatie, culoare, motor, tip_combustibil, pret)
            # Inserare în tabela "clienti"
            cursor.execute(
                "INSERT INTO masini (Marca, Modell, An_fabricatie, Culoare, Motor, Tip_combustibil, Pret) VALUES (:marca, :model, :an_fabricatie, :culoare, :motor, :tip_combustibil, :pret)",
                marca=marca, model=model, an_fabricatie=an_fabricatie, culoare=culoare,
                motor=motor, tip_combustibil=tip_combustibil, pret=pret)
            conn.commit()

            return redirect(url_for('masini'))

    except Exception as e:

        conn.rollback()
        return f"Eroare: {str(e)}"
    finally:
        cursor.close()

    return render_template('masini.html', masini=masini)

@app.route("/vanzari")
def vanzari():
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM vanzari")
        vanzari = cursor.fetchall()

        for i in range(len(vanzari)):
            vanzare = vanzari[i]
            vanzare = [round(value, 1) if isinstance(value, float) else value for value in vanzare]
            vanzari[i] = vanzare

            conn.commit()

    except Exception as e:

        conn.rollback()
        return f"Eroare: {str(e)}"
    finally:
        cursor.close()
    return render_template('vanzari.html', vanzari=vanzari)

@app.route("/garantii")
def garantii():
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM garantii")
        garantii = cursor.fetchall()

        for i in range(len(garantii)):
            garantie = garantii[i]
            garantie = [round(value, 1) if isinstance(value, float) else value for value in garantie]
            garantii[i] = garantie

            conn.commit()

    except Exception as e:

        conn.rollback()
        return f"Eroare: {str(e)}"
    finally:
        cursor.close()
    return render_template('garantii.html', garantii=garantii)

@app.route("/tip_garantii")
def tip_garantii():
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM tip_garantii")
        tip_garantii = cursor.fetchall()

        if request.method == 'POST':
            tip = request.form['tip']
            pret = request.form['pret']

            conn.commit()

            return redirect(url_for('tip_garantii'))

    except Exception as e:

        conn.rollback()
        return f"Eroare: {str(e)}"
    finally:
        cursor.close()

    return render_template('tip_garantii.html', tip_garantii=tip_garantii)

if __name__ == "__main__":
    app.run(debug=True)
    conn.close()
