#include <taskdaemon.hpp>
#include <sstream>
#include <stdexcept>
#include <string>

int main() {
    const std::string payload(100000, 'x');
    std::stringstream input;
    input << taskdaemon::json({{"task_id", "first"}, {"task_type", "echo"},
                              {"task_data", {{"message", payload}}}, {"attempt", 1}}).dump()
          << '\n';
    input << "{\"task_id\":\"second\",\"task_type\":\"retry\",\"task_data\":{},\"attempt\":2}\n";
    input << "invalid-json\n";
    std::stringstream output;
    auto* previous_input = std::cin.rdbuf(input.rdbuf());
    auto* previous_output = std::cout.rdbuf(output.rdbuf());
    taskdaemon::run([](const taskdaemon::Task& task) -> taskdaemon::Result {
        if (task.task_type == "retry") {
            return taskdaemon::error("try again", true);
        }
        return taskdaemon::success({{"task_id", task.task_id}, {"attempt", task.attempt},
                                    {"message", task.task_data.at("message")}});
    });
    std::cin.rdbuf(previous_input);
    std::cout.rdbuf(previous_output);

    std::string line;
    if (!std::getline(output, line)) throw std::runtime_error("missing success response");
    const auto success = taskdaemon::json::parse(line);
    if (success.at("status") != "success" || success.at("result").at("attempt") != 1 ||
        success.at("result").at("message") != payload) {
        throw std::runtime_error("success response lost task data or attempt label");
    }
    if (!std::getline(output, line)) throw std::runtime_error("missing retry response");
    const auto retry = taskdaemon::json::parse(line);
    if (retry.at("status") != "error" || retry.at("retryable") != true) {
        throw std::runtime_error("retry response mismatch");
    }
    if (!std::getline(output, line)) throw std::runtime_error("missing malformed-input response");
    const auto malformed = taskdaemon::json::parse(line);
    if (malformed.at("status") != "error" || malformed.at("retryable") != false) {
        throw std::runtime_error("malformed input should produce a permanent error");
    }
    if (std::getline(output, line)) throw std::runtime_error("unexpected extra response");
}
