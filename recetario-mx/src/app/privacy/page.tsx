export const metadata = {
  title: 'Politica de privacidad - Recetario MX (Skill Alexa)',
  description: 'Politica de privacidad de la skill de Alexa Recetario MX.',
};

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <article className="max-w-2xl mx-auto bg-white rounded-lg shadow p-8 text-gray-800 leading-relaxed">
        <h1 className="text-2xl font-bold text-orange-700 mb-2">
          Politica de privacidad - Recetario MX (Skill Alexa)
        </h1>
        <p className="text-gray-500 text-sm mb-8">Ultima actualizacion: febrero 2026</p>

        <p className="mb-6">
          Esta politica aplica a la skill de Alexa &quot;Recetario MX&quot; (y nombres de invocacion asociados).
        </p>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">1. Datos que recopilamos</h2>
          <p>
            Recetario MX <strong>no recopila ni almacena datos personales</strong>. No solicitamos nombre, correo, telefono ni identificadores de usuario.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">2. Uso de la voz</h2>
          <p>
            Cuando pides una receta por voz, Amazon Alexa procesa tu peticion y la envia a nuestro servicio para devolver recetas (por ejemplo: desayuno, comida, cena). Esas peticiones se procesan para generar la respuesta y no se asocian a tu identidad ni se guardan con fines de perfilado.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">3. Datos tecnicos</h2>
          <p>
            Nuestro backend puede registrar direcciones IP y metadatos de peticiones con fines operativos (errores, disponibilidad). No utilizamos estos datos para identificar usuarios ni para publicidad.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">4. Terceros</h2>
          <p>
            Las recetas se obtienen mediante busqueda en linea (Brave Search) y fuentes publicas. No compartimos datos personales con terceros porque no recopilamos datos personales.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">5. Menores</h2>
          <p>
            La skill no esta dirigida a menores de 13 anos. No recopilamos conscientemente informacion de menores.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">6. Cambios</h2>
          <p>
            Cualquier cambio relevante en esta politica se reflejara en esta pagina, con actualizacion de la fecha al pie.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">7. Contacto</h2>
          <p>
            Para dudas sobre privacidad relacionadas con Recetario MX, puedes contactar a traves del perfil de desarrollador asociado a la skill en la tienda de Alexa.
          </p>
        </section>
      </article>
    </main>
  );
}
