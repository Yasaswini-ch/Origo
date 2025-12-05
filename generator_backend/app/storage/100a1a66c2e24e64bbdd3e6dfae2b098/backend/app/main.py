from fastapi import FastAPI
app = FastAPI(title='origo-fallback-backend')

@app.get('/')
def read_root():
    return {'status': 'ok'}
