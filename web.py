from flask import Flask, render_template, request, redirect, url_for, jsonify
from peewee import *
import datetime, random
from datetime import timedelta

app = Flask(__name__)

db = "pos.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class Produk(BaseModel):
    id = AutoField(primary_key=True)
    nama_produk = CharField()
    harga_produk = IntegerField()
    gambar_produk = CharField()
    harga_produk_masuk = IntegerField()
    stok_produk = IntegerField()

class Transaksi(BaseModel):
    id = AutoField(primary_key=True)
    id_transaksi = CharField()
    id_produk = ForeignKeyField(Produk)
    nama_produk = CharField()
    jumlah_barang = IntegerField()
    tanggal_transaksi = DateTimeField()
    total_harga = IntegerField()
    profit_bersih = IntegerField()

class Cart(BaseModel):
    id = AutoField(primary_key=True)
    id_produk = ForeignKeyField(Produk)
    jumalah_barang = IntegerField()

def create_tables():
    database.create_tables({Produk, Transaksi, Cart})


def checkCart():
    cart = Cart.select()
    return len(list(cart))

@app.route("/")
def main():
    return render_template('index.html', isCart=checkCart())

@app.route("/masterbarang")
def masterbarang():
    produk = Produk.select()
    return render_template("masterbarang.html", data=produk, isCart=checkCart())

@app.route("/formmasterbarang")
def formmasterbarang():
    return render_template('formmasterbarang.html', isCart=checkCart())

@app.route("/insert", methods=['GET','POST'])
def insert():
    if request.method == "GET":
        return render_template("formmasterbarang.html")
    else:
        namaProduk = request.form['Nama_Produk']
        gambarProduk = request.form['Gambar_Produk']
        hargaProduk = request.form['Harga_Produk']
        hargaProdukMasuk = request.form['Harga_Produk_Masuk']
        stokProduk = request.form['Stok_Produk']

        Produk.create(nama_produk=namaProduk,
            harga_produk=hargaProduk, harga_produk_masuk=hargaProdukMasuk, 
            stok_produk=stokProduk, gambar_produk=gambarProduk
            )

        return redirect(url_for("masterbarang"))

@app.route('/updateproduk/<id_produk>',methods=['GET','POST'])
def updateproduk(id_produk):
    if request.method == 'GET':
        produk = Produk.select().where(Produk.id == id_produk)
        produk = produk.get()
        return render_template("updateproduk.html", data=produk, isCart=checkCart())
    else:
        namaProduk = request.form['Nama_Produk']
        gambarProduk = request.form['Gambar_Produk']
        hargaProduk = request.form['Harga_Produk']
        hargaProdukMasuk = request.form['Harga_Produk_Masuk']
        stokProduk = request.form['Stok_Produk']

        produkupdate = Produk.update(
            nama_produk=namaProduk,
            gambar_produk=gambarProduk,
            harga_produk=hargaProduk,
            harga_produk_masuk=hargaProdukMasuk,
            stok_produk=stokProduk
            ).where(Produk.id == id_produk)

        produkupdate.execute()

        return redirect(url_for("masterbarang"))

@app.route("/deleteproduk/<id_produk>")
def deleteproduk(id_produk):
    delete_produk = Produk.delete().where(Produk.id == id_produk)
    delete_produk.execute()

    return redirect(url_for("masterbarang"))

# @app.route("/search", methods=["POST"])
# def search():
    
@app.route("/cart")
def cart():
    datacart = Cart.select()
    datatotal = 0
    for i in list(datacart):
        datatotal = datatotal + i.jumalah_barang * i.id_produk.harga_produk
    return render_template('cart.html', data=datacart, total=datatotal, isCart=checkCart())

@app.route("/receipt")
def receipt():
    datacart = Cart.select()
    datatotal = 0
    datadate = datetime.datetime.now()
    for i in list(datacart):
        datatotal = datatotal + i.jumalah_barang * i.id_produk.harga_produk
    
    return render_template('receipt.html', data=datacart, total=datatotal, date=datadate)

@app.route('/add_to_cart/<id_produk>')
def addtocart(id_produk):
    cek_cart = Cart.select().where(Cart.id_produk == id_produk)
    if cek_cart.exists():
        isi_cart = cek_cart.get()
        edit_jumlah_beli = Cart.update(jumalah_barang= isi_cart.jumalah_barang+1).where(Cart.id_produk == id_produk)
        edit_jumlah_beli.execute()
        return redirect(url_for('masterbarang'))
    else:
        Cart.create(id_produk=id_produk,jumalah_barang=1)
        return redirect(url_for('masterbarang'))

@app.route('/updatecart/<id_cart>',methods=['POST','GET'])
def updatecart(id_cart):
    if request.method == 'GET':
        datacart = Cart.select().where(Cart.id == id_cart) 
        datacart = datacart.get() 
        return render_template("formmastercart.html",data=datacart, isCart=checkCart())
    else:
        jumlah_barang = request.form['Jumlah_Barang']
        cartupdate = Cart.update(jumalah_barang=jumlah_barang).where(Cart.id == id_cart)

        cartupdate.execute()

        return redirect(url_for('cart'))

@app.route('/deletecart/<id_cart>')
def deletecart(id_cart):
    deletecart = Cart.delete().where(Cart.id == id_cart)
    deletecart.execute()

    return redirect(url_for('cart'))
   
@app.route("/mastertransaksi")
def transaksi():
    data = Transaksi.select()
    dataprofit = 0
    for i in list(data):
        dataprofit = dataprofit + i.profit_bersih
    return render_template('mastertransaksi.html', data=data, profit=dataprofit, isCart=checkCart())

@app.route("/mastertransaksi/<lowdate>/<highdate>")
def transaksi_by_date(lowdate, highdate):
    endDate = datetime.datetime.strptime(highdate, "%Y-%m-%d") + timedelta(days=1)
    data = Transaksi.select().where(Transaksi.tanggal_transaksi.between(lowdate, datetime.datetime.strftime(endDate, "%Y-%m-%d")))
    dataprofit = 0
    for i in list(data):
        dataprofit = dataprofit + i.profit_bersih
    return render_template('mastertransaksi.html', data=data, profit=dataprofit, isCart=checkCart())

@app.route('/create_transaksi')
def create_transaksi():
    id_transaksi = random.randint(100000,999999)
    tanggal_transaksi = datetime.datetime.now()
    # selek cart
    datacart = Cart.select()
    for i in datacart:
        id_produk = int(str(i.id_produk))
        nama_produk = i.id_produk.nama_produk
        jumlah_barang = i.jumalah_barang
        total_harga = jumlah_barang * i.id_produk.harga_produk
        profit_bersih = total_harga - (i.id_produk.harga_produk_masuk*jumlah_barang)
        
        # update stok produk
        Update_produk = Produk.update(stok_produk=i.id_produk.stok_produk-jumlah_barang).where(Produk.id == i.id_produk)
        Update_produk.execute()

        # create transaksi
        Transaksi.create(
            id_transaksi=id_transaksi,
            id_produk=id_produk,
            nama_produk=nama_produk,
            jumlah_barang=jumlah_barang,
            total_harga=total_harga,
            profit_bersih=profit_bersih,
            tanggal_transaksi=tanggal_transaksi
        )

    # delete cart
    Deletecart = Cart.delete()
    Deletecart.execute()

    return redirect(url_for('transaksi'))


### <------------------- API ROUTES (WEBSERVICE) -------------------> ####

# API Barang
@app.route("/api/masterbarang", methods=['GET','POST', 'PUT', 'DELETE'])
def barang_api():
    if request.method == 'DELETE':
        id_produk = request.form['id_produk']
        Produk.delete().where(Produk.id == id_produk).execute()
        return jsonify({"message": "Delete Success"})

    elif request.method == 'PUT':
        id_produk = request.form['id_produk']
        nama_produk = request.form['nama_produk']
        gambar_produk = request.form['gambar_produk']
        harga_produk = request.form['harga_produk']
        harga_produk_masuk = request.form['harga_produk_masuk']
        stok_produk = request.form['stok_produk']
        Produk.update(nama_produk=nama_produk, gambar_produk=gambar_produk, harga_produk=harga_produk,harga_produk_masuk=harga_produk_masuk,stok_produk=stok_produk).where(Produk.id == id_produk).execute()
        return jsonify({"status": "success"})
    elif request.method == 'POST':
        nama_produk = request.form['nama_produk']
        gambar_produk = request.form['gambar_produk']
        harga_produk = request.form['harga_produk']
        harga_produk_masuk = request.form['harga_produk_masuk']
        stok_produk = request.form['stok_produk']
        Produk.create(nama_produk=nama_produk,gambar_produk=gambar_produk,harga_produk=harga_produk,harga_produk_masuk=harga_produk_masuk,stok_produk=stok_produk)
        return jsonify({"status": "successssss"})
    else:
        data = Produk.select()
        return jsonify(list(data.dicts()))

# API Transaksi
@app.route('/api/mastertransaksi', methods=['GET','POST'])
def transaksi_api():
    if request.method == 'POST':
        id_transaksi = random.randint(100000,999999)
        tanggal_transaksi = datetime.datetime.now()
        # selek cart
        datacart = Cart.select()
        for i in datacart:
            id_produk = int(str(i.id_produk))
            nama_produk = i.id_produk.nama_produk
            jumlah_barang = i.jumalah_barang
            total_harga = jumlah_barang * i.id_produk.harga_produk
            profit_bersih = total_harga - i.id_produk.harga_produk_masuk
            
            # update stok produk
            Update_produk = Produk.update(stok_produk=i.id_produk.stok_produk-jumlah_barang).where(Produk.id == i.id_produk)
            Update_produk.execute()

            # create transaksi
            Transaksi.create(
                id_transaksi=id_transaksi,
                id_produk=id_produk,
                nama_produk=nama_produk,
                jumlah_barang=jumlah_barang,
                total_harga=total_harga,
                profit_bersih=profit_bersih,
                tanggal_transaksi=tanggal_transaksi
            )

        # delete cart
        Deletecart = Cart.delete()
        Deletecart.execute()

        return jsonify({"status": "success"})
    else:
        data = Transaksi.select()
        dataprofit = 0
        for i in list(data):
            dataprofit = dataprofit + i.profit_bersih
        return jsonify({"data": list(data.dicts()), "total_profit_bersih": dataprofit})

#API Transaksi Berdasarkan tanggal
@app.route('/api/mastertransaksi/<startdate>/<enddate>')
def transaksi_api_by_date(startdate, enddate):
    endDate = datetime.datetime.strptime(enddate, "%Y-%m-%d") + timedelta(days=1)

    ## QUERY BERDASARKAN TANGGAL
    data = Transaksi.select().where(Transaksi.tanggal_transaksi.between(startdate, datetime.datetime.strftime(endDate, "%Y-%m-%d")))
    dataprofit = 0
    for i in list(data):
        dataprofit = dataprofit + i.profit_bersih
    return jsonify({"data": list(data.dicts()), "total_profit_bersih": dataprofit})

#API Cart
@app.route('/api/cart', methods=['GET','POST','PUT','DELETE'])
def cart_api():
    if request.method == 'POST':
        id_produk = request.form['id_produk']
        cek_cart = Cart.select().where(Cart.id_produk == id_produk)
        if cek_cart.exists():
            isi_cart = cek_cart.get()
            edit_jumlah_beli = Cart.update(jumalah_barang= isi_cart.jumalah_barang+1).where(Cart.id_produk == id_produk)
            edit_jumlah_beli.execute()
            return jsonify({"status": "success"})
        else:
            Cart.create(id_produk=id_produk,jumalah_barang=1)
            return jsonify({"status": "success"})

    elif request.method == 'PUT':
        id_produk = request.form['id_produk']
        jumlah_barang = request.form['jumlah_barang']
        Cart.update(jumalah_barang=jumlah_barang).where(Cart.id_produk == id_produk).execute()
        return jsonify({"status": "success"})

    elif request.method == 'DELETE':
        id_produk = request.form['id_produk']
        Cart.delete().where(Cart.id_produk == id_produk).execute()
        return jsonify({"status": "success"})
    else:
        datacart = Cart.select()
        datatotal = 0
        cart = []
        for i in list(datacart):
            cart.append({'nama_produk': i.id_produk.nama_produk, 'harga_produk': i.id_produk.harga_produk, 'jumlah_barang': i.jumalah_barang, 'total_harga': i.jumalah_barang * i.id_produk.harga_produk, 'gambar_produk': i.id_produk.gambar_produk})
            datatotal = datatotal + i.jumalah_barang * i.id_produk.harga_produk
        return jsonify({"data": list(cart), "total_transaksi": datatotal})

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)