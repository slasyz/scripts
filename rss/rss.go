package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"net/url"

	"github.com/PuerkitoBio/goquery"
	"github.com/gorilla/feeds"
)

type Config struct {
	Sources     []Source `json:"sources"`
	Destination string   `json:"destination"`
}

type Source struct {
	Title        string       `json:"title"`
	Name         string       `json:"name"`
	URL          string       `json:"url"`
	ParsingRules ParsingRules `json:"parsing_rules"`
}

type ParsingRules struct {
	LoopSelector  string `json:"loop_selector"`
	TitleSelector string `json:"title_selector"`
	DateSelector  string `json:"date_selector"`
	DateFormat    string `json:"date_format"`
	BodySelector  string `json:"body_selector"`
	LinkSelector  string `json:"link_selector"`
}

func main() {
	config, err := loadConfig("config.json")
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	if err := os.MkdirAll(config.Destination, 0755); err != nil {
		log.Fatalf("Error creating destination directory: %v", err)
	}

	atomFiles, err := filepath.Glob(filepath.Join(config.Destination, "*.atom"))
	if err != nil {
		log.Fatalf("Error finding .atom files: %v", err)
	}
	for _, file := range atomFiles {
		if err := os.Remove(file); err != nil {
			log.Printf("Error removing file %s: %v", file, err)
		}
	}

	for _, source := range config.Sources {
		parseSource(source, config.Destination)
	}
}

func loadConfig(filename string) (*Config, error) {
	file, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	var config Config
	err = json.Unmarshal(file, &config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}

func parseSource(source Source, destination string) {
	resp, err := http.Get(source.URL)
	if err != nil {
		log.Printf("Error fetching URL %s: %v", source.URL, err)
		return
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		log.Printf("Error parsing HTML: %v", err)
		return
	}

	feed := &feeds.Feed{
		Title:       source.Title, // Use Title instead of Name
		Link:        &feeds.Link{Href: source.URL},
		Description: fmt.Sprintf("Atom feed for %s", source.Title),
		Created:     time.Now(),
	}

	itemCount := 0

	doc.Find(source.ParsingRules.LoopSelector).Each(func(i int, s *goquery.Selection) {
		title := strings.TrimSpace(s.Find(source.ParsingRules.TitleSelector).Text())
		dateStr := strings.TrimSpace(s.Find(source.ParsingRules.DateSelector).Text())
		body := strings.TrimSpace(s.Find(source.ParsingRules.BodySelector).Text())

		var link string
		var exists bool
		if source.ParsingRules.LinkSelector != "" {
			link, exists = s.Find(source.ParsingRules.LinkSelector).Attr("href")
		} else {
			link, exists = s.Attr("href")
		}
		if !exists {
			log.Printf("Link not found for item: %s", title)
			return
		}

		parsedURL, err := url.Parse(link)
		if err != nil {
			log.Printf("Error parsing link: %v", err)
			return
		}

		baseURL, err := url.Parse(source.URL)
		if err != nil {
			log.Printf("Error parsing base URL: %v", err)
			return
		}

		resolvedURL := baseURL.ResolveReference(parsedURL).String()

		date, err := time.Parse(source.ParsingRules.DateFormat, dateStr)
		if err != nil {
			log.Printf("Selection: %s", s.Text())
			log.Printf("Error parsing date: %v", err)
			return
		}

		log.Printf("Title: '%s', URL: '%s'", title, resolvedURL)
		item := &feeds.Item{
			Title:       title,
			Link:        &feeds.Link{Href: resolvedURL},
			Description: body,
			Author:      &feeds.Author{Name: source.Title},
			Created:     date,
		}
		feed.Items = append(feed.Items, item)
		itemCount++
	})

	atom, err := feed.ToAtom()
	if err != nil {
		log.Printf("Error generating Atom feed: %v", err)
		return
	}

	outputPath := filepath.Join(destination, fmt.Sprintf("%s.atom", source.Name))
	err = os.WriteFile(outputPath, []byte(atom), 0644)
	if err != nil {
		log.Printf("Error writing Atom feed: %v", err)
	}

	log.Printf("Source: %s, Created Items: %d", source.Title, itemCount)
}
