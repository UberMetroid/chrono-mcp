from flask_restx import Api, Resource, fields, reqparse
from app.routes.api import api_bp
from app.models.database import db_service
from app.utils import validate_game_name, sanitize_input
from app.config import get_config

config = get_config()

# Create API documentation
api = Api(
    api_bp,
    title='Chrono MCP API',
    version='1.0.0',
    description='REST API for Chrono series game data analysis',
    doc='/docs',
    prefix='/api'
)

# Define models for documentation
game_model = api.model('Game', {
    'name': fields.String(description='Game identifier'),
    'display_name': fields.String(description='Human-readable game name'),
    'platforms': fields.List(fields.String, description='Available platforms'),
    'release_year': fields.Integer(description='Release year'),
    'developer': fields.String(description='Game developer'),
    'description': fields.String(description='Game description')
})

category_model = api.model('Category', {
    'name': fields.String(description='Category identifier'),
    'display_name': fields.String(description='Human-readable category name'),
    'item_count': fields.Integer(description='Number of items in category')
})

item_model = api.model('Item', {
    'data': fields.Raw(description='Item data (varies by category)'),
    'searchable_text': fields.String(description='Text for full-text search')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total_items': fields.Integer(description='Total number of items'),
    'total_pages': fields.Integer(description='Total number of pages'),
    'has_next': fields.Boolean(description='Whether there is a next page'),
    'has_prev': fields.Boolean(description='Whether there is a previous page')
})

category_response_model = api.model('CategoryResponse', {
    'game': fields.String(description='Game name'),
    'category': fields.String(description='Category name'),
    'items': fields.List(fields.Raw, description='List of items'),
    'pagination': fields.Nested(pagination_model, description='Pagination information')
})

search_result_model = api.model('SearchResult', {
    'game': fields.String(description='Game name'),
    'category': fields.String(description='Category name'),
    'item': fields.Raw(description='Matched item data')
})

search_response_model = api.model('SearchResponse', {
    'query': fields.String(description='Search query'),
    'matches': fields.List(fields.Nested(search_result_model), description='Search matches'),
    'count': fields.Integer(description='Number of matches found')
})

# Health check namespace
health_ns = api.namespace('health', description='Health check operations')

@health_ns.route('')
class Health(Resource):
    @api.doc('get_health')
    def get(self):
        """Get service health status"""
        cache_stats = {
            "hits": 0, "misses": 0, "hit_rate": 0.0,
            "total_requests": 0, "cache_size": 0
        }
        return {
            "status": "healthy",
            "timestamp": "2026-03-13T16:30:00Z",
            "version": "1.0.0",
            "cache": cache_stats
        }

# Games namespace
games_ns = api.namespace('games', description='Game operations')

@games_ns.route('')
class GamesList(Resource):
    @api.doc('list_games')
    @api.marshal_list_with(game_model)
    def get(self):
        """List all available games"""
        try:
            games = db_service.get_games()
            result = []
            for game_name in games:
                game_data = db_service.get_game_data(game_name)
                if game_data:
                    result.append({
                        'name': game_name,
                        'display_name': game_data.get('display_name', game_name),
                        'platforms': game_data.get('platforms', []),
                        'release_year': game_data.get('release_year'),
                        'developer': game_data.get('developer'),
                        'description': game_data.get('description')
                    })
            return result
        except Exception as e:
            api.abort(500, f"Database error: {str(e)}")

# Categories namespace
categories_ns = api.namespace('categories', description='Category operations')

@categories_ns.route('')
class CategoriesList(Resource):
    @api.doc('list_categories')
    @api.marshal_list_with(category_model)
    def get(self):
        """List all available categories across games"""
        try:
            categories = db_service.get_categories()
            return [{'name': cat, 'display_name': cat.replace('_', ' ').title()} for cat in categories]
        except Exception as e:
            api.abort(500, f"Database error: {str(e)}")

# Game data namespace
game_ns = api.namespace('game', description='Individual game operations')

@game_ns.route('/<game>')
@game_ns.param('game', 'Game identifier')
class GameData(Resource):
    @api.doc('get_game_data')
    @api.marshal_with(game_model)
    def get(self, game):
        """Get data for a specific game"""
        game = validate_game_name(game)
        if not game:
            api.abort(400, "Invalid game name")

        try:
            game_data = db_service.get_game_data(game)
            if not game_data:
                api.abort(404, "Game not found")

            return {
                'name': game,
                'display_name': game_data.get('display_name', game),
                'platforms': game_data.get('platforms', []),
                'release_year': game_data.get('release_year'),
                'developer': game_data.get('developer'),
                'description': game_data.get('description')
            }
        except Exception as e:
            api.abort(500, f"Database error: {str(e)}")

# Category data namespace
category_ns = api.namespace('category', description='Category data operations')

category_parser = reqparse.RequestParser()
category_parser.add_argument('page', type=int, default=1, help='Page number (default: 1)')
category_parser.add_argument('per_page', type=int, default=20, help='Items per page (default: 20, max: 100)')

@category_ns.route('/<game>/<category>')
@category_ns.param('game', 'Game identifier')
@category_ns.param('category', 'Category identifier')
class CategoryData(Resource):
    @api.doc('get_category_data')
    @api.expect(category_parser)
    @api.marshal_with(category_response_model)
    def get(self, game, category):
        """Get paginated data for a game category"""
        game = validate_game_name(game)
        category = sanitize_input(category, max_length=50)

        if not game or not category:
            api.abort(400, "Invalid parameters")

        args = category_parser.parse_args()
        page = max(1, args['page'])
        per_page = min(config.MAX_PAGE_SIZE, max(1, args['per_page']))

        try:
            result = db_service.get_category_data(game, category, page, per_page)
            if not result:
                api.abort(404, "Category not found")
            return result
        except Exception as e:
            api.abort(500, f"Database error: {str(e)}")

# Search namespace
search_ns = api.namespace('search', description='Search operations')

search_parser = reqparse.RequestParser()
search_parser.add_argument('q', required=True, help='Search query (required)')
search_parser.add_argument('game', help='Filter by game')
search_parser.add_argument('category', help='Filter by category')
search_parser.add_argument('fuzzy', type=bool, default=True, help='Use fuzzy matching')
search_parser.add_argument('threshold', type=float, default=0.6, help='Similarity threshold for fuzzy search')
search_parser.add_argument('limit', type=int, default=500, help='Maximum number of results')

@search_ns.route('')
class Search(Resource):
    @api.doc('search_items')
    @api.expect(search_parser)
    @api.marshal_with(search_response_model)
    def get(self):
        """Search across all games and categories"""
        args = search_parser.parse_args()
        query = sanitize_input(args['q'], max_length=50)

        if not query:
            api.abort(400, "Empty search query")

        try:
            matches = db_service.search_items(
                query=query,
                game_filter=args.get('game'),
                category_filter=args.get('category'),
                limit=min(args.get('limit', 500), 1000)  # Cap at 1000
            )

            return {
                "query": query,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            api.abort(500, f"Search error: {str(e)}")

# Export namespace
export_ns = api.namespace('export', description='Data export operations')

@export_ns.route('/<game>')
@export_ns.param('game', 'Game identifier')
class ExportGame(Resource):
    @api.doc('export_game')
    @api.produces(['application/json'])
    def get(self, game):
        """Export complete game data as JSON"""
        game = validate_game_name(game)
        if not game:
            api.abort(400, "Invalid game name")

        try:
            game_data = db_service.get_game_data(game)
            if not game_data:
                api.abort(404, "Game not found")

            from flask import Response, jsonify
            response = jsonify(game_data)
            response.headers['Content-Disposition'] = f'attachment; filename={game}.json'
            return response
        except Exception as e:
            api.abort(500, f"Export error: {str(e)}")

@export_ns.route('/<game>/<category>')
@export_ns.param('game', 'Game identifier')
@export_ns.param('category', 'Category identifier')
class ExportCategory(Resource):
    @api.doc('export_category')
    @api.produces(['application/json'])
    def get(self, game, category):
        """Export category data as JSON"""
        game = validate_game_name(game)
        category = sanitize_input(category, max_length=50)

        if not game or not category:
            api.abort(400, "Invalid parameters")

        try:
            result = db_service.get_category_data(game, category, 1, 10000)  # Get all items
            if not result:
                api.abort(404, "Category not found")

            from flask import Response, jsonify
            response = jsonify(result['items'])
            response.headers['Content-Disposition'] = f'attachment; filename={game}_{category}.json'
            return response
        except Exception as e:
            api.abort(500, f"Export error: {str(e)}")

@export_ns.route('/<game>/<category>/csv')
@export_ns.param('game', 'Game identifier')
@export_ns.param('category', 'Category identifier')
class ExportCategoryCSV(Resource):
    @api.doc('export_category_csv')
    @api.produces(['text/csv'])
    def get(self, game, category):
        """Export category data as CSV"""
        game = validate_game_name(game)
        category = sanitize_input(category, max_length=50)

        if not game or not category:
            api.abort(400, "Invalid parameters")

        try:
            result = db_service.get_category_data(game, category, 1, 10000)  # Get all items
            if not result:
                api.abort(404, "Category not found")

            import csv
            import io
            from flask import Response

            items = result['items']
            if not items:
                api.abort(404, "No data to export")

            output = io.StringIO()
            if isinstance(items[0], dict):
                fieldnames = list(items[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(items)
            else:
                writer = csv.writer(output)
                writer.writerow(['value'])
                for item in items:
                    writer.writerow([item])

            response = Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename={game}_{category}.csv'
                }
            )
            return response
        except Exception as e:
            api.abort(500, f"Export error: {str(e)}")

# Plot namespace
plot_ns = api.namespace('plot', description='Plot/story operations')

@plot_ns.route('')
class PlotList(Resource):
    @api.doc('list_plots')
    def get(self):
        """List available plot trees"""
        from pathlib import Path
        from app.config import get_config

        config = get_config()
        extracted_dir = config.EXTRACTED_DIR
        if not extracted_dir.exists():
            return {"plots": []}

        plots = []
        for f in extracted_dir.glob('*_plot_tree.json'):
            game_name = f.stem.replace('_plot_tree', '').replace('_', ' ').title()
            if 'ct' in f.stem.lower():
                game_name = 'Chrono Trigger'
            elif 'cc' in f.stem.lower():
                game_name = 'Chrono Cross'
            elif 'rd' in f.stem.lower():
                game_name = 'Radical Dreamers'

            plots.append({
                "game": game_name,
                "file": f"/api/plot/{f.stem.replace('_plot_tree', '')}"
            })

        return {"plots": plots}

@plot_ns.route('/<plot_id>')
@plot_ns.param('plot_id', 'Plot identifier (ct, cc, rd)')
class PlotDetail(Resource):
    @api.doc('get_plot')
    def get(self, plot_id):
        """Get plot tree data"""
        plot_id = sanitize_input(plot_id, max_length=50)
        if '..' in plot_id or '/' in plot_id:
            api.abort(400, "Invalid plot ID")

        # Map IDs to filenames
        id_map = {
            "ct": "ct_plot_tree.json",
            "chrono_trigger": "ct_plot_tree.json",
            "cc": "cc_plot_tree.json",
            "chrono_cross": "cc_plot_tree.json",
            "rd": "rd_plot_tree.json",
            "radical_dreamers": "rd_plot_tree.json"
        }

        filename = id_map.get(plot_id.lower())
        if not filename:
            api.abort(404, "Plot not found")

        from app.config import get_config
        config = get_config()
        filepath = config.EXTRACTED_DIR / filename
        if not filepath.exists():
            api.abort(404, "Plot file not found")

        try:
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            api.abort(500, f"Error reading plot: {str(e)}")

# Media namespace
media_ns = api.namespace('media', description='Media operations')

@media_ns.route('/images')
class ImagesList(Resource):
    @api.doc('list_images')
    def get(self):
        """List available images"""
        from pathlib import Path
        from app.config import get_config

        config = get_config()
        art_dir = config.DATA_DIR / "art"
        if not art_dir.exists():
            return {"images": []}

        images = []
        for f in art_dir.glob('*'):
            if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                images.append({
                    "name": f.name,
                    "path": f"/data/art/{f.name}"
                })

        return {"images": images[:200]}

@media_ns.route('/audio')
class AudioList(Resource):
    @api.doc('list_audio')
    def get(self):
        """List available audio files"""
        from pathlib import Path
        from app.config import get_config

        config = get_config()
        audio_dir = config.DATA_DIR / "audio"
        if not audio_dir.exists():
            return {"audio": []}

        audio = []
        for f in audio_dir.glob('*'):
            if f.suffix.lower() in ['.wav', '.mp3', '.ogg']:
                audio.append({
                    "name": f.name,
                    "path": f"/data/audio/{f.name}"
                })

        return {"audio": audio[:100]}