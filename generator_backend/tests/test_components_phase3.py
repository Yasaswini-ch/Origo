import io
from zipfile import ZipFile

def test_save_component_and_zip_includes(client):
    # Generate a base project
    r = client.post('/generate', json={
        'idea': 'Comp Save',
        'target_users': 'devs',
        'features': 'x',
        'stack': 'react+fastapi',
    })
    assert r.status_code == 200
    project_id = r.json()['project_id']

    # Save a component into the project
    comp = {
        'component_name': 'ExtraWidget.jsx',
        'component_code': "export default function Extra(){return <div/>}"
    }
    r2 = client.post(f'/projects/{project_id}/components', json=comp)
    assert r2.status_code == 200
    body = r2.json()
    assert body['component_path'] == 'src/components/ExtraWidget.jsx'
    md = body['metadata']
    assert 'src/components/ExtraWidget.jsx' in md['frontend_files']

    # Download zip and verify component present
    rz = client.get(f'/projects/{project_id}/download')
    assert rz.status_code == 200
    buf = io.BytesIO(rz.content)
    with ZipFile(buf) as z:
        names = z.namelist()
        assert any(n.endswith('frontend/src/components/ExtraWidget.jsx') for n in names)
