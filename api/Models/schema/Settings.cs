using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace api.Models
{
    public class Settings
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }

        [BsonElement("ChatId")]
        public string ChatId { get; set; }

        [BsonElement("Currency")]
        public string Currency { get; set; }

        [BsonElement("SalaryDay")]
        public int? SalaryDay { get; set; }
    }
}
