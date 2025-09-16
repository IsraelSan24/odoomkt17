async function apiperu_dni(dni) {
  const url = "https://apiperu.dev/api/dni";
  const token = "4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479";
  const headers = {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
  try {
    const params = { dni: String(dni) };
    const params_json = JSON.stringify(params);
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: params_json,
    });
    if (response.ok) {
      const data = await response.json();
      const access_data = data.data;
      return [
        access_data.nombre_completo,
        access_data.nombres,
        access_data.apellido_paterno,
        access_data.apellido_materno,
      ];
    } else {
      console.error(`Error ${response.status}`);
      console.error(await response.text());
    }
  } catch (error) {
    console.error(`Error ${error}`);
  }
}

async function consultarDNI() {
  const dni = document.getElementById("dni").value;
  if (dni) {
    try {
      const [nombre_completo, nombres, apellido_paterno, apellido_materno] =
        await apiperu_dni(dni);
      const first_name = nombres.split(" ")[0];
      document.getElementById("first_name").value = first_name;
      console.log(document.getElementById("first_name").value);
      console.log(first_name);
      console.log(nombres);
      console.log(nombre_completo);
      document.getElementById("last_name").value =
        apellido_paterno + " " + apellido_materno;
      console.log(document.getElementById("last_name").value);
    } catch (error) {
      console.error("Error al consultar el DNI:", error);
    }
  } else {
    console.error("Ingrese un número de DNI");
  }
}