import { FastifyInstance } from "fastify";
import { suggest } from "../services/suggestionService";

export async function suggestionRoutes(app: FastifyInstance) {
  app.get("/v1/suggestions", async (request) => {
    const query = request.query as { q?: string; storeChainId?: string };
    const q = query.q ?? "";

    const mockedPrefs = {
      userId: "demo-user",
      climateWeight: 30,
      healthWeight: 35,
      ethicsWeight: 10,
      animalWeight: 10,
      financeWeight: 15,
    };

    return {
      data: suggest(q, mockedPrefs, query.storeChainId),
      meta: {
        query: q,
      },
    };
  });
}
