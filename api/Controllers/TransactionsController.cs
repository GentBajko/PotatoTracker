using api.Models;
using api.Services;
using Microsoft.AspNetCore.Mvc;
using MongoDB.Bson;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;

namespace api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TransactionsController : ControllerBase
    {
        private readonly TransactionService _transactionService;
        private readonly ILogger<TransactionsController> _logger;

        public TransactionsController(TransactionService transactionService, ILogger<TransactionsController> logger)
        {
            _transactionService = transactionService;
            _logger = logger;
        }

        [HttpGet("{chatId}")]
        public ActionResult<List<Transaction>> GetTransactions(string chatId)
        {
            _logger.LogInformation("GetTransactions called");
            var transactions = _transactionService.Get(chatId);
            return Ok(transactions);
        }

        [HttpGet("{chatId}/{id}")]
        public ActionResult<Transaction> GetTransaction(string chatId, string id)
        {
            if (!ObjectId.TryParse(id, out ObjectId objectId))
            {
                return BadRequest("Invalid transaction ID format.");
            }

            var transaction = _transactionService.Get(chatId, objectId);
            if (transaction == null)
                return NotFound();

            return Ok(transaction);
        }

        [HttpGet("{chatId}/history")]
        public ActionResult<History> GetHistory(string chatId)
        {
            var history = _transactionService.GetHistory(chatId);
            return Ok(history);
        }

        [HttpPost]
        public ActionResult<Transaction> CreateTransaction(Transaction transaction)
        {
            var createdTransaction = _transactionService.Create(transaction);
            return CreatedAtAction(nameof(GetTransaction), new { chatId = createdTransaction.ChatId, id = createdTransaction.Id.ToString() }, createdTransaction);
        }

        [HttpPut("{chatId}/{id}")]
        public IActionResult UpdateTransaction(string chatId, string id, Transaction transaction)
        {
            if (!ObjectId.TryParse(id, out ObjectId objectId))
            {
                return BadRequest("Invalid transaction ID format.");
            }

            _transactionService.Update(chatId, objectId, transaction);
            return NoContent();
        }

        [HttpDelete("{chatId}/{id}")]
        public IActionResult DeleteTransaction(string chatId, string id)
        {
            if (!ObjectId.TryParse(id, out ObjectId objectId))
            {
                return BadRequest("Invalid transaction ID format.");
            }

            _transactionService.Remove(chatId, objectId);
            return NoContent();
        }
    }
}
