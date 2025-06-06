import pickle
import re # <--- PENTING: Tambahkan ini untuk fungsi clean_text
import os # <--- PENTING: Tambahkan ini untuk path file

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Mengaktifkan CORS untuk semua route

# --- PENTING: Sesuaikan PATH model dan vectorizer ---
# Pastikan file model dan vectorizer berada di folder yang sama dengan app.py (yaitu di dalam folder 'backend').
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'sentiment_model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

model = None
vectorizer = None

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as model_file:
            model = pickle.load(model_file)
        print(f"Model berhasil dimuat dari: {MODEL_PATH}")
    else:
        print(f"Error: File model tidak ditemukan di: {MODEL_PATH}")
        # Anda bisa memilih untuk keluar atau mengatur model menjadi None dan menangani kesalahan nanti
        # exit() # Jika Anda ingin aplikasi gagal total saat start jika model tidak ditemukan
        model = None

    if os.path.exists(VECTORIZER_PATH):
        with open(VECTORIZER_PATH, 'rb') as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
        print(f"Vectorizer berhasil dimuat dari: {VECTORIZER_PATH}")
    else:
        print(f"Error: File vectorizer tidak ditemukan di: {VECTORIZER_PATH}")
        # exit() # Jika Anda ingin aplikasi gagal total saat start jika vectorizer tidak ditemukan
        vectorizer = None

    if model and hasattr(model, 'classes_'):
        print(f"Kelas model yang diketahui: {model.classes_}")
    else:
        print("Model dimuat tetapi properti 'classes_' tidak ditemukan atau model belum dimuat.")

except Exception as e:
    print(f"Error saat memuat model atau vectorizer: {e}")
    # exit() # Keluar jika ada error lain saat memuat
    model = None
    vectorizer = None

# Fungsi clean_text harus didefinisikan di level teratas atau di dalam kelas/fungsi lain
# daripada di dalam route, agar tidak didefinisikan berulang kali pada setiap request.
def clean_text(text_input):
    # Menghapus HTML tags
    text_input = re.sub(r'<.*?>', '', text_input)
    # Menghapus karakter non-alfabet
    text_input = re.sub(r'[^a-zA-Z\s]', '', text_input)
    # Mengubah ke huruf kecil
    text_input = text_input.lower()
    return text_input

@app.route('/api/predict_sentiment', methods=['POST']) # <--- Perbarui endpoint
def predict_sentiment():
    if model is None or vectorizer is None:
        return jsonify({'error': 'Backend tidak siap: Model atau Vectorizer tidak dapat dimuat. Silakan cek log deployment.'}), 500

    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Permintaan harus berupa JSON dan mengandung kunci "text"'}), 400

    text = request.json['text']

    try:
        cleaned_text = clean_text(text)
        text_vectorized = vectorizer.transform([cleaned_text])

        sentiment_label = model.predict(text_vectorized)[0] # Akan mengembalikan 'positive' atau 'negative'

        sentiment_score = 0.0
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(text_vectorized)[0]
            try:
                predicted_class_index = list(model.classes_).index(sentiment_label)
                sentiment_score = probabilities[predicted_class_index] # <--- Perbaikan di sini
            except ValueError:
                print(f"Warning: Predicted sentiment '{sentiment_label}' not found in model classes {model.classes_}")
                sentiment_score = 0.0

        return jsonify({
            'text': text,
            'sentiment': sentiment_label,
            'sentiment_score': round(float(sentiment_score), 4)
        })
    except Exception as e:
        # Lebih detail dalam log error
        print(f"Error during sentiment processing: {e}")
        return jsonify({'error': f'Terjadi kesalahan saat memproses sentimen: {str(e)}'}), 500

# --- Fungsi Handler Vercel ---
# Ini adalah fungsi yang akan dipanggil Vercel saat request datang.
# JANGAN UBAH NAMA FUNGSI INI.
def handler(request, context):
    # Impor ini di dalam fungsi untuk menghindari masalah impor sirkular
    # atau masalah yang tidak perlu saat tidak dijalankan oleh Vercel.
    from werkzeug.serving import WSGIRequestHandler
    from werkzeug.wrappers import Request as WSGIRequest, Response as WSGIResponse

    # Membangun lingkungan WSGI dari objek permintaan Vercel
    # Vercel `request` objek berbeda dari Flask `request` objek
    environ = WSGIRequest(request.environ).environ

    # Panggil aplikasi Flask Anda
    response = app.wsgi_app(environ, lambda status, headers: WSGIResponse(status, headers))

    # Mengonversi respons Flask ke format respons yang diharapkan Vercel
    return WSGIResponse(response.get_data(), headers=response.headers, status=response.status_code)


# --- Untuk pengembangan lokal (Opsional) ---
if __name__ == '__main__':
    print("Menjalankan Flask API di http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)