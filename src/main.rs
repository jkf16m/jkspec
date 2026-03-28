use std::fs;
use std::io::Write;
use std::path::Path;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() > 1 && args[1] == "init" {
        let spec_dir = ".jkspec";
        let project_json = "{\n  \"name\": \"your_project\"\n}";
        let ai_json = "{\n  \"llm\": \"gpt-4\"\n}";
        if !Path::new(spec_dir).exists() {
            fs::create_dir(spec_dir).expect("Failed to create .jkspec directory");
        }
        let mut pj = fs::File::create(format!("{}/project.json", spec_dir)).expect("Failed to create project.json");
        pj.write_all(project_json.as_bytes()).expect("Failed to write project.json");
        let mut aj = fs::File::create(format!("{}/ai.json", spec_dir)).expect("Failed to create ai.json");
        aj.write_all(ai_json.as_bytes()).expect("Failed to write ai.json");
        println!("Initialized .jkspec with project.json and ai.json");
    } else {
        println!("Usage: jkspec init");
    }
}

