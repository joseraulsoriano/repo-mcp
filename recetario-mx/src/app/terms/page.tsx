export const metadata = {
  title: 'Terminos de uso - Recetario MX (Skill Alexa)',
  description: 'Terminos de uso de la skill de Alexa Recetario MX.',
};

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <article className="max-w-2xl mx-auto bg-white rounded-lg shadow p-8 text-gray-800 leading-relaxed">
        <h1 className="text-2xl font-bold text-orange-700 mb-2">
          Terminos de uso - Recetario MX (Skill Alexa)
        </h1>
        <p className="text-gray-500 text-sm mb-8">Ultima actualizacion: febrero 2026</p>

        <p className="mb-6">
          Al usar la skill de Alexa &quot;Recetario MX&quot; aceptas los siguientes terminos.
        </p>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">1. Descripcion del servicio</h2>
          <p>
            Recetario MX es una skill de Alexa que sugiere recetas (por ejemplo desayuno, comida, cena) y puede ofrecer informacion sobre ingredientes y precios. El contenido se obtiene de fuentes publicas y busqueda en linea. No garantizamos la exactitud nutricional ni de precios.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">2. Uso aceptable</h2>
          <p>
            Debes usar la skill de forma lícita y solo para uso personal o domestico. No esta permitido usar el servicio para fines comerciales no autorizados, ni extraer datos de forma automatizada de manera que sobrecargue nuestros sistemas.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">3. Contenido e informacion</h2>
          <p>
            Las recetas y la informacion mostrada tienen caracter orientativo. El desarrollador no se hace responsable de decisiones tomadas en base a este contenido (por ejemplo dietas, alergias o compras). Siempre verifica fuentes oficiales cuando la informacion sea critica.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">4. Disponibilidad</h2>
          <p>
            El servicio se ofrece &quot;tal cual&quot;. Nos reservamos el derecho de modificar, suspender o discontinuar la skill o partes de ella, sin obligacion de aviso previo.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">5. Alexa y Amazon</h2>
          <p>
            El uso de la skill esta sujeto tambien a los terminos y politicas de Amazon y Alexa. Recetario MX es un servicio independiente y no esta respaldado por Amazon.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">6. Cambios</h2>
          <p>
            Podemos actualizar estos terminos en cualquier momento. La version vigente sera la publicada en esta pagina. El uso continuado de la skill tras cambios constituye la aceptacion de los nuevos terminos.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mt-6 mb-2">7. Contacto</h2>
          <p>
            Para preguntas sobre estos terminos puedes contactar a traves del perfil de desarrollador de la skill en la tienda de Alexa.
          </p>
        </section>
      </article>
    </main>
  );
}
