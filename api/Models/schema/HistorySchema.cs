using System.Text.Json.Serialization;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace api.Models.schema
{
    public class HistorySchema
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }
        [JsonPropertyName("chatId")]
        public string? ChatId { get; set; }
        [JsonPropertyName("transactions")]
        public Transaction[]? Transactions { get; set; }

        public HistorySchema() {
            Id = ObjectId.GenerateNewId().ToString();
        }
    }
}