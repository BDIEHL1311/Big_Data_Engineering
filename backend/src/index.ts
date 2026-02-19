import Fastify from "fastify";
import { suggestionRoutes } from "./routes/suggestions";

const app = Fastify({ logger: true });

app.get("/health", async () => ({ ok: true, service: "backend" }));
app.get("/v1/health", async () => ({ ok: true, version: "v1" }));
app.register(suggestionRoutes);

const start = async () => {
  try {
    const port = Number(process.env.PORT ?? 3000);
    await app.listen({ port, host: "0.0.0.0" });
  } catch (error) {
    app.log.error(error);
    process.exit(1);
  }
};

void start();
