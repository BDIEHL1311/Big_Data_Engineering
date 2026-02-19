export interface OutboxMutation {
  entity: "shopping_list" | "list_item";
  operation: "create" | "update" | "delete";
  payload: Record<string, unknown>;
  clientMutationId: string;
  baseRevision: number;
  localTimestamp: string;
}

export const syncPolicy = {
  checkedConflict: "last_write_wins",
  textConflict: "server_wins_with_client_marker",
};

export async function pushAndPull(cursor: string, outbox: OutboxMutation[]) {
  return {
    pushed: outbox.length,
    newCursor: `${cursor}-next`,
    policy: syncPolicy,
  };
}
