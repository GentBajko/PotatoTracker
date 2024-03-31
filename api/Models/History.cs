namespace api.Models
{
    public class History
    {
        public string? ChatId { get; set; }
        public List<Transaction>? Transactions { get; set; }
    }
}